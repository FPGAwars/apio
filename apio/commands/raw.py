# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO RAW command"""

import click
from click.core import Context
from apio import util


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The raw command allows to bypass  apio and run underlying
tools directly. This is an advanced command that requires familiarity
with the underlying tools.

\b
Examples:
  apio raw "yosys --version"                          # yosys version
  apio raw "nextpnr-ice40 --version"                  # nextpnr version
  apio raw "yosys -p 'read_verilog leds.v; show' -q"  # Graph a module
  apio raw "verilator --lint-only  leds.v"            # lint a module

[Note] If you find a raw command that would benefit other apio users
consider suggesting it as an apio feature request.
"""


@click.command(
    "raw",
    short_help="Execute commands directly from the Apio packages.",
    help=HELP,
    context_settings=util.context_settings(),
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

    exit_code = util.call(cmd)
    ctx.exit(exit_code)
