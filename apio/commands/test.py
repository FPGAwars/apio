# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio test' command"""

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
The sim command simulates one or all the testbenches in the project
and is useful for automatic unit testing of the code. Testbenches
are expected have a name ending with _tb (e.g my_module_tb.v) and to exit
with the $fatal directive if any error is detected. The commands is typically
used in the root directory of the project that contains the apio.ini.

\b
Examples
  apio test                 # Run all *_tb.v testbenches.
  apio test my_module_tb.v  # Run a single testbench

It is recommanded NOT to use the `$dumpfile()` function in your testbenchs as
this may override the default name and location of the generated .vcd file.

For a sample testbench that is compatible with apio see the
example at
https://github.com/FPGAwars/apio-examples/tree/master/upduino31/testbench

[Hint] To simulate the testbench with a graphical visualizaiton of the
signals see the 'apio sim' command.
"""


@click.command(
    "test",
    short_help="Test all or a single verilog testbench module.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@click.argument("testbench_file", nargs=1, required=False)
@options.project_dir_option
# @options.testbench
def cli(
    _: click.core.Context,
    # Arguments
    testbench_file: str,
    # Options
    project_dir: Path,
):
    """Implements the test command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(project_dir=project_dir, load_project=True)

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    exit_code = scons.test({"testbench": testbench_file})
    sys.exit(exit_code)
