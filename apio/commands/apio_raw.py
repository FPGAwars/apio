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
from click import secho
from apio import pkg_util, cmd_util
from apio.apio_context import ApioContext, ApioContextScope
from apio.commands import options
from apio.util import nameof


# ---------------------------
# -- COMMAND
# ---------------------------
APIO_RAW_HELP = """
The command ‘apio raw’ allows you to bypass Apio and run underlying tools
directly. This is an advanced command that requires familiarity with the
underlying tools.

Before running the command, Apio temporarily modifies system environment
variables such as $PATH to provide access to its packages. To view these
environment changes, run the command `apio raw --env`.

\b
Examples:
  apio raw -- yosys --version           # Yosys version
  apio raw -v -- yosys --version        # Same but with verbose apio info.
  apio raw -- yosys                     # Run Yosys in interactive mode.
  apio raw -- icepll -i 12 -o 30        # Calc ICE PLL
  apio raw --env                        # Show apio env setting.
  apio raw -h                           # Print this help info.

The -- token is used to separate Apio commands and their arguments from the
underlying tools and their arguments. It can be omitted in some cases, but
it’s a good practice to always use it. As a rule of thumb, always prefix the
raw command you want to run with 'apio raw -- '.
"""


env_option = click.option(
    "env",  # Var name.
    "-e",
    "--env",
    is_flag=True,
    help="Show the apio env changes.",
    cls=cmd_util.ApioOption,
)


@click.command(
    name="raw",
    short_help="Execute commands directly from the Apio packages.",
    help=APIO_RAW_HELP,
    context_settings={"ignore_unknown_options": True},
)
@click.pass_context
@click.argument("cmd", metavar="COMMAND", nargs=-1, type=click.UNPROCESSED)
@env_option
@options.verbose_option
def cli(
    cmd_ctx: click.Context,
    # Arguments
    cmd: Tuple[str],
    # Options
    env: bool,
    verbose: bool,
):
    """Implements the apio raw command which executes user
    specified commands from apio installed tools.
    """

    # -- Prohibit cmd and --env together, for no specific reason.
    cmd_util.check_at_most_one_param(cmd_ctx, nameof(env, cmd))

    # -- Convert the tuple of strings to a list of strings.
    cmd: List[str] = list(cmd)

    if not cmd and not env:
        cmd_util.fatal_usage_error(cmd_ctx, "Missing an option or a command")

    # -- Set the system env for the packages. This both dumps the env settings
    # -- if --env option is specifies and prepare the env for the command
    # -- execution below.
    if cmd or env:
        apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)
        pkg_util.set_env_for_packages(
            apio_ctx, quiet=not (env or verbose), verbose=env or verbose
        )

    if cmd:
        # -- Make sure that at least the oss-cad-suite is installed.
        pkg_util.check_required_packages(apio_ctx, ["oss-cad-suite"])

        # -- Echo the commands. The apio raw command is platform dependent
        # -- so this may help us and the user diagnosing issues.
        if verbose:
            secho(f"\n---- Executing {cmd}:")

        # -- Invoke the command.
        try:
            exit_code = subprocess.call(cmd, shell=False)
        except FileNotFoundError as e:
            secho(f"{e}", fg="red")
            sys.exit(1)

        if verbose:
            secho("----\n")
            if exit_code != 0:
                secho(f"Exist status [{exit_code}] ERROR", fg="red")
            else:
                secho("Exit status [0] OK", fg="green")

        # -- Return the command's status code.
        sys.exit(exit_code)

    sys.exit(0)
