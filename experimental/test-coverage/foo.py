import os
import subprocess
from pathlib import Path


def launch_child():
    """Launch foo.main() as a subprocess."""
    print("*** Parent: Launching child...")

    # -- Get the path to the SConstruct file.
    sconst_path = os.path.join(os.path.dirname(__file__), "SConstruct")
    print(f"*** Parent: SConstruct = {sconst_path}")

    # -- Change dir away from the sconstruct file,
    os.chdir("..")

    # -- Run the scons subprocess
    subprocess.run(["python", "-m", "SCons", "-f", sconst_path])
    print("*** Parent: back from child.")


def called_from_scons():
    """Called from SConstruct to print a message"""
    print("*** Child: called from scons")
    print(f"*** Child: current dir: {os.getcwd()}")



