#!venv/bin/python
"""Apio starting point."""

import sys


def main():
    """Apio starting point."""

    # pylint: disable=import-outside-toplevel

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

    # -- Else, this is a normal apio invocation. Call the top level Apio's
    # -- Click command. We import apio only in this case.
    else:
        from apio.commands.apio import apio_top_cli

        # -- Due to the Click decorations of apio_top_cli() and the Click
        # -- magic, this function is not really invoked but Click dispatches
        # -- it to its subcommands that was selected by the user command line.
        apio_top_cli()


if __name__ == "__main__":
    main()
