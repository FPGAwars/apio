"""A script to build the apio pyinstaller package for the current platform.

Prerequisites
* Python is available.
* This apio local repo is installed as the pip apio package.
  (run 'pip install -e .' at the root of this repo.)
* The Pyinstaller package is installed ('pip install pyinstaller').

Usage:
  python ./build.py
"""

from pathlib import Path
import shutil
from subprocess import CompletedProcess, run
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils import util

apio_version = util.get_apio_version()

apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)
platform_id = apio_ctx.platform_id
print(f"\nPlatform id = [{platform_id}]")

NAME = "apio-" + platform_id.replace("_", "-") + "-" + apio_version
print(f"\nPackage name = [{NAME}]")


dist = Path("_dist")
work = Path("_work")

# -- Clean old build dirs.
for path in [dist, work]:
    if path.is_dir():
        print(f"Deleting old dir [{path}].")
        shutil.rmtree(path)
    else:
        print(f"Dir [{path}] does not exist.")
    assert not path.exists(), path


# -- Run the pyinstaller
cmd = [
    "pyinstaller",
    "--distpath",
    str(dist),
    "--workpath",
    str(work),
    "./apio.spec",
]
print(f"\nRun: {cmd}")
result: CompletedProcess = run(cmd)
assert result.returncode == 0, "Pyinstaller exited with an error code."
print("Pyinstaller completed successfully")

# -- Change to _dist directory
# print("Changing cwd to _dist.")
# os.chdir("_dist")

# -- Rename the dist directory.
main = dist / "main"
package = dist / NAME
print(f"\nRenaming [{str(main)}] to [{str(package)}]")
shutil.move(main, package)

# -- Add the darwin activate file.

resources = Path("resources")
if apio_ctx.is_darwin:
    print(f"\nWriting darwin activate file.")
    shutil.copyfile(resources / "darwin-activate", package / "activate")

# -- Add readme file.
print(f"\nWriting the README.txt file.")
shutil.copyfile(resources / "README.txt", package / "README.txt")

# -- Zip package
print("\nCompressing the package.")
zip_fname = shutil.make_archive(package, "zip", package)
print(f"\nCreated {zip_fname}.")
