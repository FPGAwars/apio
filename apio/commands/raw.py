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
from varname import nameof
import click
from apio import pkg_util, cmd_util
from apio.apio_context import ApioContext


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The raw command allows to bypass  apio and run underlying
tools directly. This is an advanced command that requires familiarity
with the underlying tools. Before running the command, apio changes the
internal env settings to provide access to its packages. To view the
env changes, run `apio raw --env'.

\b
Examples:
  apio raw yosys --version                                # Yosys version
  apio raw -- nextpnr-ice40 --help                        # Nextpnr help
  apio raw yosys -f verilog -p "show -format dot" main.v  # Graph a module
  apio raw icepll -i 12 -o 30                             # Calc ICE PLL
  apio raw --env                                          # Show env

The '--' token may be used to seperate between apio arguments and the
commands arguments (e.g. '-h' or '--help').
"""


verbose_option = click.option(
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
    cls=cmd_util.ApioCommand,
    context_settings={"ignore_unknown_options": True},
)
@click.pass_context
@click.argument("cmd", metavar="COMMAND", nargs=-1, type=click.UNPROCESSED)
@verbose_option
def cli(
    cmd_ctx: click.core.Context,
    # Arguments
    cmd: Tuple[str],
    # Options
    env: bool,
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
        pkg_util.set_env_for_packages(apio_ctx, verbose=env)

    if cmd:
        # -- Make sure that at least the oss-cad-suite is installed.
        pkg_util.check_required_packages(apio_ctx, ["oss-cad-suite"])

        # -- Echo the commands. The apio raw command is platform dependent
        # -- so this may help us and the user diagnosing issues.
        click.secho(f"cmd = {cmd}")

        # -- Invoke the command.
        try:
            exit_code = subprocess.call(cmd, shell=False)
        except FileNotFoundError as e:
            click.secho(f"{e}", fg="red")
            sys.exit(1)

        if exit_code != 0:
            click.secho(f"Exist status [{exit_code}] ERROR", fg="red")
        else:
            click.secho("Exit status [0] OK", fg="green")

        # -- Return the command's status code.
        sys.exit(exit_code)

    sys.exit(0)
