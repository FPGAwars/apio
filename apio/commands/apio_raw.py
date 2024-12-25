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
from apio import pkg_util, cmd_util
from apio.apio_context import ApioContext
from apio.commands import options
from apio.util import nameof


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The raw command allows to bypass  apio and run underlying
tools directly. This is an advanced command that requires familiarity
with the underlying tools.

Before running the command, apio changes temporarly
system env vars such as $PATH to provide access to its packages. To view those
env changes, run `apio raw --env'.

\b
Examples:
  apio raw -- yosys --version           # Yosys version
  apio raw -v -- yosys --version        # Same but with verbose apio info.
  apio raw -- yosys                     # Run Yosys in interactive mode.
  apio raw -- icepll -i 12 -o 30        # Calc ICE PLL
  apio raw --env                        # Show apio env setting.
  apio raw -h                           # Print this help info.

The '--' token is used  to seperate between apio commands and its argument
and the executed command and its arguments. It can be ommited in some cases
but it's a good paractice to always use it. As a rule of thumb, prepend the
command you want to run with 'apio raw -- ' and it should work.
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
    "raw",
    short_help="Execute commands directly from the Apio packages.",
    help=HELP,
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
        apio_ctx = ApioContext(load_project=False)
        pkg_util.set_env_for_packages(
            apio_ctx, quiet=not (env or verbose), verbose=env or verbose
        )

    if cmd:
        # -- Make sure that at least the oss-cad-suite is installed.
        pkg_util.check_required_packages(apio_ctx, ["oss-cad-suite"])

        # -- Echo the commands. The apio raw command is platform dependent
        # -- so this may help us and the user diagnosing issues.
        if verbose:
            click.secho(f"\n---- Executing {cmd}:")

        # -- Invoke the command.
        try:
            exit_code = subprocess.call(cmd, shell=False)
        except FileNotFoundError as e:
            click.secho(f"{e}", fg="red")
            sys.exit(1)

        if verbose:
            click.secho("----\n")
            if exit_code != 0:
                click.secho(f"Exist status [{exit_code}] ERROR", fg="red")
            else:
                click.secho("Exit status [0] OK", fg="green")

        # -- Return the command's status code.
        sys.exit(exit_code)

    sys.exit(0)
