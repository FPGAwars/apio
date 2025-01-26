# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio raw' command"""

import sys
import subprocess
from typing import Tuple, List
import click
from apio.common.apio_console import cout
from apio.apio_context import ApioContext, ApioContextScope
from apio.commands import options
from apio.utils import cmd_util, pkg_util
from apio.utils.util import nameof
from apio.managers import installer


# ---------------------------
# -- COMMAND
# ---------------------------
APIO_RAW_HELP = """
The command ‘apio raw’ allows you to bypass Apio and run underlying tools
directly. This is an advanced command that requires familiarity with the
underlying tools.

Before running the command, Apio temporarily modifies system environment
variables such as $PATH to provide access to its packages. To view these
environment changes, run the command with the -v option.

\b
Examples:
  apio raw -- yosys --version           # Yosys version
  apio raw -v -- yosys --version        # Same but with verbose apio info.
  apio raw -- yosys                     # Run Yosys in interactive mode.
  apio raw -- icepll -i 12 -o 30        # Calc ICE PLL
  apio raw -v                           # Show apio env setting.
  apio raw -h                           # Show this help info.

The -- token is used to separate Apio commands and their arguments from the
underlying tools and their arguments. It can be omitted in some cases, but
it’s a good practice to always use it. As a rule of thumb, always prefix the
raw command you want to run with 'apio raw -- '.
"""


@click.command(
    name="raw",
    short_help="Execute commands directly from the Apio packages.",
    help=APIO_RAW_HELP,
    context_settings={"ignore_unknown_options": True},
)
@click.pass_context
@click.argument("cmd", metavar="COMMAND", nargs=-1, type=click.UNPROCESSED)
@options.verbose_option
def cli(
    cmd_ctx: click.Context,
    # Arguments
    cmd: Tuple[str],
    # Options
    verbose: bool,
):
    """Implements the apio raw command which executes user
    specified commands from apio installed tools.
    """
    # -- At lease one of -v and cmd should be specified.
    cmd_util.check_at_least_one_param(cmd_ctx, nameof(verbose, cmd))

    # -- Create an apio context. We don't care about an apio project.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- If needed, install missing packages.
    if cmd:
        installer.install_missing_packages_on_the_fly(apio_ctx)

    # -- Set the env for packages. If verbose, also dumping the env changes
    # -- in a user friendly way.
    pkg_util.set_env_for_packages(apio_ctx, quiet=not verbose, verbose=verbose)

    # -- If no command, we are done.
    if not cmd:
        sys.exit(0)

    # -- Convert the tuple of strings to a list of strings.
    cmd: List[str] = list(cmd)

    # -- Echo the commands. The apio raw command is platform dependent
    # -- so this may help us and the user diagnosing issues.
    if verbose:
        cout(f"\n---- Executing {cmd}:")

    # -- Invoke the command.
    try:
        exit_code = subprocess.call(cmd, shell=False)
    except FileNotFoundError as e:
        cout(f"{e}", style="red")
        sys.exit(1)

    if verbose:
        cout("----\n")
        if exit_code == 0:
            cout("Exit status [0] OK", style="green")

        else:
            cout(f"Exist status [{exit_code}] ERROR", style="red")

    # -- Return the command's status code.
    sys.exit(exit_code)
