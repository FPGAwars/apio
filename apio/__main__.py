#!venv/bin/python
"""Apio starting point."""

import sys
import os
import atexit

# -- Since this module is used also as the entry point for the scons
# -- subprocess, we don't add here dependency on util.py and use a light
# -- weight debug env var detection.
# -- Set APIO_DEBUG=1 to enable.
debug_enabled = int(os.environ.get("APIO_DEBUG", "0")) > 0


def on_exit(msg):
    """Prints a debug message on process exit. The msg string is passed
    from the handler registrations below.
    """
    if debug_enabled:
        print(msg)


def main():
    """Apio starting point."""

    if debug_enabled:
        print(f"Apio main(): original argv: {sys.argv}")

    # pylint: disable=import-outside-toplevel

    # -- Handle the case of the scons subprocess. Because we also use
    # -- pyinstaller, without standard pip packages, we can't simply invoke
    # -- the 'scons' binary so we invoke the SCons module from the apio main.
    # -- See more details at:
    # -- See https://github.com/orgs/pyinstaller/discussions/9023.
    # --
    # -- In this case argv goes through these stages
    # -- Original:                 <binary> -m apio --scons ...
    # -- Under python:             <binary> --scons ...
    # -- Under pyinstaller:        <binary> -m apio --scons ...
    # -- After fixing for scons:   <binary> ...
    # --
    # -- Notice that the -m apio args are automatically removed by the
    # -- python interpreter but are preserved by the pyinstaller, hence
    # -- the two cases.
    python_scons = sys.argv[1:2] == ["--scons"]
    pyinstaller_scons = sys.argv[1:4] == ["-m", "apio", "--scons"]

    if debug_enabled:
        print(f"Apio main(): {python_scons=}")
        print(f"Apio main(): {pyinstaller_scons=}")

    if python_scons or pyinstaller_scons:

        if debug_enabled:
            print("Apio main(): this is an scons process")

        # -- Since scons_main() doesn't return, we use this handler to print
        # -- an exit message for debugging.
        atexit.register(on_exit, "Apio main(): scons process exit")

        # -- Import and initialize scons only when running the scons
        # -- subprocess.
        from SCons.Script.Main import main as scons_main
        from apio.common.common_util import maybe_wait_for_remote_debugger

        # -- If system env var APIO_SCONS_DEBUGGER is defined, regardless of
        # -- its value, we wait on a remote debugger to be attached, e.g.
        # -- from Visual Studio Code.
        # --
        # -- You can place a breakpoint for example at SconsHandler.start().
        maybe_wait_for_remote_debugger("APIO_SCONS_DEBUGGER")

        # -- Drop the scons trigger args
        if python_scons:
            # -- Case 1: Using a python interpreter which already dropped
            # -- the ["-m", "apio"].  Dropping just ["--scons"]
            sys.argv[1:] = sys.argv[2:]
        else:
            # -- Case 2: Using pyinstaller which preserved the ["-m", "apio"].
            # -- Dropping ["-m", "apio", "--scons"]
            sys.argv[1:] = sys.argv[4:]

        if debug_enabled:
            print(f"Apio main(): scons fixed argv: {sys.argv}")

        # -- Invoke the scons main function. It gets the modified argv from sys
        # -- and doesn't return.
        scons_main()

    # -- Handle the case of a normal apio invocation.
    else:
        if debug_enabled:
            print("Apio main(): this is an apio process")

        # -- Since apio_top_cli() doesn't return, we use this handler to print
        # -- an exit message for debugging.
        atexit.register(on_exit, "Apio main(): apio process exit")

        # -- Import the apio CLI only when running the apio process
        # -- (as opposed to the scons sub process).
        from apio.commands.apio import apio_top_cli

        # -- Due to the Click decorations of apio_top_cli() and the Click
        # -- magic, this function is not really invoked but Click dispatches
        # -- it to its subcommands that was selected by the user command line.
        # -- This function call doesn't return.
        apio_top_cli()


if __name__ == "__main__":
    main()
