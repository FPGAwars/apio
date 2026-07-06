# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio raw' command"""

import sys
import subprocess
from typing import Tuple, List
import click
from apio.common.apio_console import cout, cerror
from apio.common.apio_styles import SUCCESS, ERROR, INFO
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.commands import options
from apio.utils import cmd_util
from apio.utils.cmd_util import ApioCommand

# ----------- apio raw


def run_command_with_possible_elevation(arg_list: List[str]) -> int:
    """
    Runs a command and returns its exit code.

    On all platforms the command is executed with its arguments passed
    verbatim as an argv list (no intermediate shell that would
    re-tokenize them) and with the caller's current directory.

    On Windows, if the executable's manifest requires elevation (e.g.
    zadig), the direct execution fails with ERROR_ELEVATION_REQUIRED
    and we retry through cmd.exe which triggers the UAC prompt.
    """
    if not arg_list:
        return 0  # nothing to run

    try:
        return subprocess.call(arg_list, shell=False)

    # Specific common errors — give user-friendly feedback
    except FileNotFoundError:
        cout(f"Error: Command not found → {arg_list[0]}", style=ERROR)
        return 127

    except OSError as e:
        # -- Windows only: ERROR_ELEVATION_REQUIRED. Unlike CreateProcess,
        # -- cmd.exe falls back to ShellExecute which shows the UAC
        # -- elevation prompt. Passing the args as a list (not a joined
        # -- string) lets subprocess apply proper Windows quoting.
        if getattr(e, "winerror", None) == 740:
            return subprocess.call(["cmd.exe", "/c"] + arg_list, shell=False)

        if isinstance(e, PermissionError):
            cout(f"Error: Permission denied → {arg_list[0]}", style=ERROR)
            return 126

        raise


# -- Text in the rich-text format of the python rich library.
APIO_RAW_HELP = """
The command 'apio raw' allows you to bypass Apio and run underlying tools \
directly. This is an advanced command that requires familiarity with the \
underlying tools.

Before running the command, Apio temporarily modifies system environment \
variables such as '$PATH' to provide access to its packages. To view these \
environment changes, run the command with the '-v' option.

Examples:[code]
  apio raw    -- yosys --version      # Yosys version
  apio raw -v -- yosys --version      # Verbose apio info.
  apio raw    -- yosys                # Yosys interactive mode.
  apio raw    -- icepll -i 12 -o 30   # Calc ICE PLL.
  apio raw    -- which yosys          # Lookup a command.
  apio raw    -- bash                 # Open a shell with Apio's env.
  apio raw    -- zadig                # Run Zadig (on Windows).
  apio raw -v                         # Show apio env setting.
  apio raw -h                         # Show this help info.[/code]

The marker '--' must separate between the arguments of the apio \
command itself and those of the executed command.
"""


@click.command(
    name="raw",
    cls=ApioCommand,
    short_help="Execute commands directly from the Apio packages.",
    help=APIO_RAW_HELP,
    context_settings={"ignore_unknown_options": True},
)
@click.pass_context
@click.argument("cmd", metavar="COMMAND", nargs=-1, type=click.UNPROCESSED)
@options.verbose_option
def cli(
    cmd_ctx: click.Context,
    *,
    # Arguments
    cmd: Tuple[str],
    # Options
    verbose: bool,
):
    """Implements the apio raw command which executes user
    specified commands from apio installed tools.
    """

    # -- If the user specifies a raw command, verify that the '--' separator
    # -- exists and that all the command tokens were specified after it.
    # -- Ideally Click should be able to validate it but it doesn't (?).
    if cmd:

        # -- Locate the first '--' in argv. None if not found.
        dd_index = next((i for i, x in enumerate(sys.argv) if x == "--"), None)

        # -- If the '--' separator was not specified this is an error.
        if dd_index is None:
            cerror("The raw command separator '--' was not found.")
            cout(
                "The raw command should be specified after a '--' separator.",
                "Type 'apio raw -h' for details.",
                style=INFO,
            )
            sys.exit(1)

        # -- Number of command tokens after the "--"
        n_after = len(sys.argv) - dd_index - 1

        # -- Command tokens that where specified before the '--'
        tokens_before = list(cmd)[: len(cmd) - n_after]

        # -- Should have no command tokens before the "--"
        if tokens_before:
            cerror(f"Invalid arguments: {tokens_before}.")
            cout(
                "Did you mean to have them after the '--' separator?",
                "See 'apio raw -h' for details.",
                style=INFO,
            )
            sys.exit(1)

    # -- At lease one of -v and cmd should be specified.
    cmd_util.check_at_least_one_param(cmd_ctx, ["verbose", "cmd"])

    # -- Create an apio context. We don't care about an apio project.
    # -- Using config and packages because we want the binaries in the apio
    # -- packages to be available for the 'apio raw' command.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
    )

    # -- Set the env for packages. If verbose, also dumping the env changes
    # -- in a user friendly way.
    apio_ctx.set_env_for_packages(quiet=not verbose, verbose=verbose)

    # -- If no command, we are done.
    if not cmd:
        sys.exit(0)

    # -- Convert the tuple of strings to a list of strings.
    _cmd: List[str] = list(cmd)

    # -- Echo the commands. The apio raw command is platform dependent
    # -- so this may help us and the user diagnosing issues.
    if verbose:
        cout(f"\n---- Executing {_cmd}:")

    # -- Invoke the command.
    exit_code = run_command_with_possible_elevation(_cmd)

    if verbose:
        cout("----\n")
        if exit_code == 0:
            cout("Exit status [0] OK", style=SUCCESS)

        else:
            cout(f"Exist status [{exit_code}] ERROR", style=ERROR)

    # -- Return the command's status code.
    sys.exit(exit_code)
