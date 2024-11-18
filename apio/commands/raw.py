# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio raw' command"""

import click
from apio import util, pkg_util, cmd_util
from apio.apio_context import ApioContext


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
    cmd_ctx: click.core.Context,
    # Arguments
    cmd: str,
    # Options
    env: bool,
):
    """Implements the apio raw command which executes user
    specified commands from apio installed tools.
    """

    if not cmd and not env:
        cmd_util.fatal_usage_error(cmd_ctx, "Missing an option or a command")

    # -- Set the system env for the packages. This both dumps the env settings
    # -- if --env option is specifies and prepare the env for the command
    # -- execution below.
    if cmd or env:
        apio_ctx = ApioContext(project_scope=False)
        pkg_util.set_env_for_packages(apio_ctx, verbose=env)

    if cmd:
        # -- Make sure that at least the oss-cad-suite is installed.
        pkg_util.check_required_packages(apio_ctx, ["oss-cad-suite"])

        # -- Invoke the command.
        exit_code = util.call(cmd)
        cmd_ctx.exit(exit_code)

    cmd_ctx.exit(0)
