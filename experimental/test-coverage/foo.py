import os
import sys
import subprocess


def launch_child():
    """Launch foo.main() as a subprocess."""
    print("*** Parent: Launching child...")

    # -- Get the path to the SConstruct file.
    sconst_path = os.path.join(os.path.dirname(__file__), "SConstruct")
    print(f"*** Parent: SConstruct = {sconst_path}")

    # -- Change dir away from the sconstruct file,
    os.chdir("/tmp")

    # -- Run the scons subprocess
    subprocess.run([sys.executable, "-m", "SCons", "-f", sconst_path, "build"])

    proc = subprocess.Popen(
        [sys.executable, "-m", "SCons", "-f", sconst_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = proc.communicate()

    assert proc.returncode == 0, proc.returncode

    print("*** Parent: back from child.")


if __name__ == "__main__":
    launch_child()
