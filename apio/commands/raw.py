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
from apio import util
from apio import pkg_util
from apio import cmd_util


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The raw command allows to bypass  apio and run underlying
tools directly. This is an advanced command that requires familiarity
with the underlying tools.

\b
Examples:
  apio raw "yosys --version"                          # Yosys version
  apio raw "nextpnr-ice40 --version"                  # Nextpnr version
  apio raw "yosys -p 'read_verilog leds.v; show' -q"  # Graph a module
  apio raw "verilator --lint-only  leds.v"            # Lint a module
  apio raw "icepll -i 12 -o 30"                       # ICE PLL parameters

[Note] If you find a raw command that would benefit other apio users
consider suggesting it as an apio feature request.
"""


@click.command(
    "raw",
    short_help="Execute commands directly from the Apio packages.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@click.argument("cmd")
def cli(
    ctx: Context,
    # Arguments
    cmd: str,
):
    """Implements the apio raw command which executes user
    specified commands from apio installed tools.
    """
    pkg_util.set_env_for_packages()
    exit_code = util.call(cmd)
    ctx.exit(exit_code)
