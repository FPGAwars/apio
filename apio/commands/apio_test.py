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
from apio.common.apio_console import cout
from apio.common.apio_styles import EMPH1
from apio.managers.scons_manager import SConsManager
from apio.commands import options
from apio.common.proto.apio_pb2 import ApioTestParams
from apio.utils import cmd_util
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)


# --------- apio test


# -- Text in the rich-text format of the python rich library.
APIO_TEST_HELP = """
The command 'apio test' simulates one or all the testbenches in the project \
and is useful for automated testing of your design. Testbenches are expected \
to have names ending with _tb (e.g., my_module_tb.v) and should exit with the \
'$fatal' directive if an error is detected.

Examples:[code]
  apio test                  # Run all *_tb.v and *_tb.sv testbenches.
  apio test my_module_tb.v   # Run a single testbench.
  apio test my_module_tb.sv  # Run a single System Verilog testbench.
  apio test util/led_tb.v    # Run a testbench in a sub-folder.
  apio test --default        # Run only the default testbench.[/code]

[NOTE] Testbench specification is always the testbench file path relative to \
the project directory, even if using the '--project-dir' option.

[IMPORTANT] Do not use the Verilog '$dumpfile()' function in your \
testbenches, as this may override the default name and location Apio sets \
for the generated .vcd file.

The default testbench is the same that is used by the 'apio sim' command \
which is the one specified in 'apio.ini' using the 'default-testbench' \
option, or the only testbench, if the project contains exactly one \
testbnech.

For a sample testbench compatible with Apio features, see: \
https://github.com/FPGAwars/apio-examples/tree/master/upduino31/testbench

[b][Hint][/b] To simulate a testbench with a graphical visualization \
of the signals, refer to the 'apio sim' command.
"""

option_default = click.option(
    "default",
    "-d",
    "--default",
    is_flag=True,
    help="Test only the default testbench",
    cls=cmd_util.ApioOption,
)


@click.command(
    name="test",
    cls=cmd_util.ApioCommand,
    short_help="Test all or a single verilog testbench module.",
    help=APIO_TEST_HELP,
)
@click.pass_context
@click.argument(
    "testbench-path",
    metavar="[TESTBENCH-PATH]",
    nargs=1,
    required=False,
)
@option_default
@options.env_option_gen()
@options.project_dir_option
def cli(
    cmd_ctx: click.Context,
    # Arguments
    testbench_path: str,
    # Options
    default: bool,
    env: Optional[str],
    project_dir: Optional[Path],
):
    """Implements the test command."""

    cmd_util.check_at_most_one_param(cmd_ctx, ["default", "testbench_path"])

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

    # -- If default is specified, try to get the default file from apio.ini,
    # -- note that if that is not define, we pass this command invocation
    # -- anyway to scons, in case there is exactly one testbench file.
    if default:
        # -- If the option is not specified, testbench is set to None and
        # -- we issue an error message in the scons process.
        testbench_path = apio_ctx.project.get_str_option(
            "default-testbench", None
        )
        if testbench_path:
            cout(f"Using default testbench: {testbench_path}", style=EMPH1)

    # -- Construct the test params
    test_params = ApioTestParams(
        testbench_path=testbench_path if testbench_path else None,
        default_option=default,
    )

    exit_code = scons.test(test_params)
    sys.exit(exit_code)
