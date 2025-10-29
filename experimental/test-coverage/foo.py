# foo.py
import os
import sys
import subprocess
from pathlib import Path


def launch_child():
    """Launch foo.main() as a subprocess."""
    print("*** Parent: Launching child...")
    subprocess.run(["python", "-m", "foo"])
    print("*** Parent: back from child.")


def main():
    """Child process main function"""
    print("*** Child: main() called")
    sys.exit(0)


# Subprocess entry point
if __name__ == "__main__":
    main()
