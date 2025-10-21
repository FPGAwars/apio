# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio test' command"""

import sys
from typing import Optional
from pathlib import Path
import click
from apio.managers.scons_manager import SConsManager
from apio.commands import options
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.common.proto.apio_pb2 import ApioTestParams
from apio.utils import cmd_util


# --------- apio test


# -- Text in the rich-text format of the python rich library.
APIO_TEST_HELP = """
The command 'apio test' simulates one or all the testbenches in the project \
and is useful for automated testing of your design. Testbenches are expected \
to have names ending with _tb (e.g., my_module_tb.v) and should exit with the \
'$fatal' directive if an error is detected.

Examples:[code]
  apio test                 # Run all *_tb.v testbenches.
  apio test my_module_tb.v  # Run a single testbench.[/code]

[NOTE] Testbench specification is always the testbench file path relative to \
the project directory, even if using the '--project-dir' option.

[IMPORTANT] Avoid using the Verilog '$dumpfile()' function in your \
testbenches, as this may override the default name and location Apio sets \
for the generated .vcd file.

For a sample testbench compatible with Apio features, see: \
https://github.com/FPGAwars/apio-examples/tree/master/upduino31/testbench

[b][Hint][/b] To simulate a testbench with a graphical visualization \
of the signals, refer to the 'apio sim' command.
"""


@click.command(
    name="test",
    cls=cmd_util.ApioCommand,
    short_help="Test all or a single verilog testbench module.",
    help=APIO_TEST_HELP,
)
@click.pass_context
@click.argument("testbench_file", nargs=1, required=False)
@options.env_option_gen()
@options.project_dir_option
# @options.testbench
def cli(
    _: click.Context,
    # Arguments
    testbench_file: str,
    # Options
    env: Optional[str],
    project_dir: Optional[Path],
):
    """Implements the test command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.PROJECT_REQUIRED,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        project_dir_arg=project_dir,
        env_arg=env,
    )

    # -- Create the scons manager.
    scons = SConsManager(apio_ctx)

    # -- Construct the test params
    test_params = ApioTestParams(
        testbench=testbench_file if testbench_file else None
    )

    exit_code = scons.test(test_params)
    sys.exit(exit_code)
