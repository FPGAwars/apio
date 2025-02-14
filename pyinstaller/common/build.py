from pathlib import Path
import shutil
import os
from subprocess import CompletedProcess, run
import sys

# -- Allows to import apio ctx.
sys.path.append("../../..")
from apio.apio_context import ApioContext, ApioContextScope

apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)
platform_id = apio_ctx.platform_id
print(f"\nPlatform id = [{platform_id}]")

NAME = "apio-" + platform_id
print(f"\nPackage name = [{NAME}]")


DARWIN_ACTIVATE="""
# run 'source activate' to enable the apio executable.
#
echo "Please wait"
echo "Removing quarantine flags in this directory."
sudo find . -exec xattr -d com.apple.quarantine {} 2> /dev/null \;
echo "Done"
"""

README="""
1. Run 'source activate' once to enable the executables.
2. Add this directory to your PATH.
3. Use the 'apio' command. For example, 'apio -h' for help.
"""

# -- Clean old build dirs.
for dir in ["_dist", "_build"]:
    path = Path(dir)
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
        "_dist",
        "--workpath",
        "_build",
        "./apio.spec",
    ]
print(f"\nRun: {cmd}")
result: CompletedProcess = run(
    cmd
)
assert result.returncode == 0, "Pyinstaller exited with an error code."
print("Pyinstaller completed successfully")

# -- Change to _dist directory
print("Changing cwd to _dist.")
os.chdir("_dist")

# -- Rename the dist directory.
print(f"\nRenaming [_dist/main] to [_dist/{NAME}]")
shutil.move("main", NAME)

# -- Add activate file.
if apio_ctx.is_darwin:
    print(f"\nWriting {NAME}/activate.")
    with open(f"{NAME}/activate", "w") as file:
        file.write(DARWIN_ACTIVATE.lstrip())

# -- Add readme file.
print(f"\nWriting {NAME}README.txt.")
with open(f"{NAME}/README.txt", "w") as file:
    file.write(README.lstrip())

# -- Zip package
print("\nCompressing package.")
zip_fname = shutil.make_archive(NAME, "zip", NAME)
print(f"\nCreated {zip_fname}.")

