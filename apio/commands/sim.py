# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio sim' command"""

import sys
from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import cmd_util
from apio.commands import options
from apio.apio_context import ApioContext


# ---------------------------
# -- COMMAND
# ---------------------------

HELP = """
The sim command simulates a testbench file and shows
the simulation results a GTKWave graphical window. The testbench is expected
to have a name ending with _tb (e.g. my_module_tb.v) and the
commands is typically used in the root directory
of the project that contains the apio.ini file and it
accepts the testbench file name as an argument. For example:

\b
Example:
  apio sim my_module_tb.v
  apio sim my_module_tb.v --force

It is recommanded NOT to use the `$dumpfile()` function in your testbenchs as
this may override the default name and location of the generated .vcd file.

The sim command defines the INTERACTIVE_SIM that can be used in the testbench
to distinguise between 'apio test' and 'apio sim', for example to ignore error
with 'apio sim' and view the erronous signals gtkwave. For a sample testbench
that uses those macro see the example at
https://github.com/FPGAwars/apio-examples/tree/master/upduino31/testbench

[Hint] when you configure the signals in GTKWave, you can save the
configuration for future invocations.
"""


@click.command(
    "sim",
    short_help="Simulate a testbench with graphic results.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@click.argument("testbench", nargs=1, required=True)
@options.force_option_gen(help="Force simulation.")
@options.project_dir_option
def cli(
    _: click.core.Context,
    # Arguments
    testbench: str,
    # Options
    force: bool,
    project_dir: Path,
):
    """Implements the apio sim command. It simulates a single testbench
    file and shows graphically the signal graphs.
    """

    # -- Create the apio context.
    apio_ctx = ApioContext(project_dir=project_dir, load_project=True)

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # -- Simulate the project with the given parameters
    exit_code = scons.sim({"testbench": testbench, "force_sim": force})

    # -- Done!
    sys.exit(exit_code)
