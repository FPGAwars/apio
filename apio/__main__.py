#!venv/bin/python
"""Apio starting point."""

import sys

# pylint: disable=import-outside-toplevel


def main():
    """Apio starting point."""

    # -- Handle the case in which we run under pyinstaller and the pyinstaller
    # -- program was invoked to run the scons subprocess. This case doesn't
    # -- happen when running as a standard pip package.
    # -- See https://github.com/orgs/pyinstaller/discussions/9023 for details.
    if sys.argv[1:3] == ["-m", "SCons"]:
        # -- Drop the "-m SCons" args.
        sys.argv[1:] = sys.argv[3:]
        # -- We import and initialize scons only when running the scons
        # -- subprocess.
        from SCons.Script.Main import main as scons_main

        # Invoke the scons main function.
        scons_main()

    # -- Else, this is a normal apio invocation. Call the top level click
    # -- command. We import apio only in this case.
    else:
        from apio.commands.apio import cli as apio

        apio()


if __name__ == "__main__":
    main()
