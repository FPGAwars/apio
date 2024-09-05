# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO SIM command"""

from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import util
from apio.commands import options

# ---------------------------
# -- COMMAND
# ---------------------------

HELP = """
The apio sim command simulates a given testbench file and shows
the simulation results a GTKWave graphical window. A typical invocation
is done in the PFGA project directory where the apio.ini file and the verilog
source files resides. The command accepts the testbench file name as
an argument. For example:

  apio sim my_module_tb.v

The apio sim command defines the verilog macro INTERACTIVE_SIM. The
presernce of this macro allows testbenches to continue and display the
simulation signals instead of aborting the simulation.

Hint: when you configure the signals in GTKWave, you can save the
configuration for future invocations.
"""


@click.command(
    "sim",
    short_help="Simulate a testbench with graphic results.",
    help=HELP,
    context_settings=util.context_settings(),
)
@click.pass_context
@click.argument("testbench", nargs=1)
@options.project_dir_option
def cli(
    ctx,
    # Arguments
    testbench: str,
    # Options
    project_dir: Path,
):
    """Implements the apio sim command. It simulates a single testbench
    file and shows graphically the signal graphs.
    """

    # -- Create the scons object
    scons = SCons(project_dir)

    # -- Simulate the project with the given parameters
    exit_code = scons.sim({"testbench": testbench})

    # -- Done!
    ctx.exit(exit_code)
