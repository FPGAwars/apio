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
from apio.commands import options
from apio.apio_context import ApioContext, ApioContextScope
from apio.common.proto.apio_pb2 import ApioTestParams


# ---------------------------
# -- COMMAND
# ---------------------------
APIO_TEST_HELP = """
The command ‘apio test’ simulates one or all the testbenches in the project
and is useful for automated testing of your design. Testbenches are expected
to have names ending with _tb (e.g., my_module_tb.v) and should exit with the
$fatal directive if an error is detected.

\b
Examples
  apio test                 # Run all *_tb.v testbenches.
  apio test my_module_tb.v  # Run a single testbench

[Important] Avoid using the Verilog $dumpfile() function in your testbenches,
as this may override the default name and location Apio sets for the
generated .vcd file.

For a sample testbench compatible with Apio features, see:
https://github.com/FPGAwars/apio-examples/tree/master/upduino31/testbench

[Hint] To simulate a testbench with a graphical visualization of the signals,
refer to the ‘apio sim’ command.
"""


@click.command(
    name="test",
    short_help="Test all or a single verilog testbench module.",
    help=APIO_TEST_HELP,
)
@click.pass_context
@click.argument("testbench_file", nargs=1, required=False)
@options.project_dir_option
# @options.testbench
def cli(
    _: click.Context,
    # Arguments
    testbench_file: str,
    # Options
    project_dir: Path,
):
    """Implements the test command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_REQUIRED, project_dir_arg=project_dir
    )

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # -- Construct the test params
    test_params = ApioTestParams(
        testbench=testbench_file if testbench_file else None
    )

    exit_code = scons.test(test_params)
    sys.exit(exit_code)
