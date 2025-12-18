# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio sim' command"""

import sys
from typing import Optional
from pathlib import Path
import click
from apio.common.apio_console import cout
from apio.common.apio_styles import EMPH1
from apio.managers.scons_manager import SConsManager
from apio.commands import options
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.common.proto.apio_pb2 import SimParams
from apio.utils import cmd_util


# --------- apio sim


# -- Text in the rich-text format of the python rich library.
APIO_SIM_HELP = """
The command 'apio sim' simulates the default or the specified testbench file \
and displays its simulation results in a graphical GTKWave window. \
The testbench is expected to have a name ending with _tb, such as \
'main_tb.v' or 'main_tb.sv'. The default testbench file can be specified \
using the apio.ini option 'default-testbench'. If 'default-testbench' is not \
specified and the project has exactly one testbench file, that file will be \
used as the default testbench.

Example:[code]
  apio sim                   # Simulate the default testbench.
  apio sim my_module_tb.v    # Simulate the specified testbench.
  apio sim my_module_tb.sv   # Simulate the specified testbench.
  apio sim --no-gtkwave      # Simulate but skip GTKWave.
  apio sim --detach          # Launch and forget gtkwave.[/code]

[IMPORTANT] Avoid using the Verilog '$dumpfile()' function in your \
testbenches, as this may override the default name and location Apio sets \
for the generated .vcd file.

[NOTE] Testbench specification is always the testbench file path relative to \
the project directory, even if using the '--project-dir' option.

The sim command defines the macro 'APIO_SIM=1' which can be used by \
testbenches to skip `$fatal` statements to have the simulation continue and \
generate signals for the GTKWave viewer.

[code]# Instead of this
$fatal;

# Use this
if (!`APIO_SIM) $fatal;[/code]

[b][Hint][/b] When configuring the signals in GTKWave, save the \
configuration so you don’t need to repeat it each time you run the \
simulation.
"""

no_gtkw_wave_option = click.option(
    "no_gtkwave",  # Var name.
    "-n",
    "--no-gtkwave",
    is_flag=True,
    help="Skip GTKWave",
    cls=cmd_util.ApioOption,
)

detach_option = click.option(
    "detach",  # Var name.
    "-d",
    "--detach",
    is_flag=True,
    help="Launch and forget GTKWave.",
    cls=cmd_util.ApioOption,
)


@click.command(
    name="sim",
    cls=cmd_util.ApioCommand,
    short_help="Simulate a testbench with graphic results.",
    help=APIO_SIM_HELP,
)
@click.pass_context
@click.argument("testbench", nargs=1, required=False)
@options.force_option_gen(short_help="Force simulation.")
@options.env_option_gen()
@no_gtkw_wave_option
@detach_option
@options.project_dir_option
def cli(
    _: click.Context,
    # Arguments
    testbench: str,
    # Options
    force: bool,
    env: Optional[str],
    no_gtkwave: bool,
    detach: bool,
    project_dir: Optional[Path],
):
    """Implements the apio sim command. It simulates a single testbench
    file and shows graphically the signal graphs.
    """

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments

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

    # -- If testbench not given, try to get a default from apio.ini.
    if not testbench:
        # -- If the option is not specified, testbench is set to None and
        # -- we issue an error message in the scons process.
        testbench = apio_ctx.project.get_str_option("default-testbench", None)
        if testbench:
            cout(f"Using default testbench: {testbench}", style=EMPH1)

    # -- Construct the scons sim params.
    sim_params = SimParams(
        testbench=testbench,
        force_sim=force,
        no_gtkwave=no_gtkwave,
        detach_gtkwave=detach,
    )

    # -- Simulate the project with the given parameters
    exit_code = scons.sim(sim_params)

    # -- Done!
    sys.exit(exit_code)
