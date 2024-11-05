# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio raw' command"""

import click
from click.core import Context
from apio import util, pkg_util, cmd_util
from apio.resources import Resources


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The raw command allows to bypass  apio and run underlying
tools directly. This is an advanced command that requires familiarity
with the underlying tools. Before running the command, apio changes the
internal env settings to provide access to its packages. To view the
env changes, use the --env option.

\b
Examples:
  apio raw "yosys --version"                          # Yosys version
  apio raw "nextpnr-ice40 --version"                  # Nextpnr version
  apio raw "yosys -p 'read_verilog leds.v; show' -q"  # Graph a module
  apio raw "verilator --lint-only  leds.v"            # Lint a module
  apio raw "icepll -i 12 -o 30"                       # ICE PLL parameters
  apio raw --env                                      # Show env changes
  apio raw --env "yosys --version"                    # Show also env changes


[Note] If you find a raw command that would benefit other apio users
consider suggesting it as an apio feature request.
"""

verbose_option = click.option(
    "env",  # Var name.
    "-e",
    "--env",
    is_flag=True,
    help="Show env changes.",
    cls=cmd_util.ApioOption,
)


@click.command(
    "raw",
    short_help="Execute commands directly from the Apio packages.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@click.argument("cmd", metavar="COMMAND", required=False)
@verbose_option
def cli(
    ctx: Context,
    # Arguments
    cmd: str,
    # Options
    env: bool,
):
    """Implements the apio raw command which executes user
    specified commands from apio installed tools.
    """

    if not cmd and not env:
        cmd_util.fatal_usage_error(ctx, "Missing an option or a command")

    # -- Set the system env for using the packages.
    pkg_util.set_env_for_packages(verbose=env)

    # -- Make sure the oss-cad-suite is installed.
    if cmd:
        resources = Resources()
        pkg_util.check_required_packages(["oss-cad-suite"], resources)
        exit_code = util.call(cmd)
    else:
        exit_code = 0

    ctx.exit(exit_code)
