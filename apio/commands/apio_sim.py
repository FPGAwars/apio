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
from click import secho
from apio.managers.scons import SCons
from apio.commands import options
from apio.apio_context import ApioContext, ApioContextScope


# ---------------------------
# -- COMMAND
# ---------------------------

APIO_SIM_HELP = """
The command ‘apio sim’ simulates the default or the specified testbench file
and displays its simulation results in a graphical GTKWave window.
The testbench is expected to have a name ending with _tb, such as
main_tb.v or main_tb.sv. The default testbench file can be specified using
the apio.ini option ‘default-testbench’. If 'default-testbench' is not
specified and the project has exactly one testbench file, that file will be
used as the default testbench.

\b
Example:
  apio sim                        # Simulate the default testbench file.
  apio sim my_module_tb.v         # Simulate the specified testbench file.

[Important] Avoid using the Verilog $dumpfile() function in your testbenches,
as this may override the default name and location Apio sets for the
generated .vcd file.

The sim command defines the INTERACTIVE_SIM macro, which can be used in the
testbench to distinguish between ‘apio test’ and ‘apio sim’. For example,
you can use this macro to ignore certain errors when running with ‘apio sim’
and view the erroneous signals in GTKWave.

For a sample testbench that utilizes this macro, see the example at:
https://github.com/FPGAwars/apio-examples/tree/master/upduino31/testbench

[Hint] When configuring the signals in GTKWave, save the configuration so you
don’t need to repeat it each time you run the simulation.
"""


@click.command(
    name="sim",
    short_help="Simulate a testbench with graphic results.",
    help=APIO_SIM_HELP,
)
@click.pass_context
@click.argument("testbench", nargs=1, required=False)
@options.force_option_gen(help="Force simulation.")
@options.project_dir_option
def cli(
    _: click.Context,
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
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_REQUIRED,
        project_dir_arg=project_dir,
    )

    # -- If testbench not given, try to get a default from apio.ini.
    if not testbench:
        # -- If the option is not specified, testbench is set to None and
        # -- we issue an error message in the scons process.
        testbench = apio_ctx.project.get("default-testbench", None)
        if testbench:
            secho(f"Using default testbench: {testbench}", fg="cyan")

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # -- Simulate the project with the given parameters
    exit_code = scons.sim({"testbench": testbench, "force_sim": force})

    # -- Done!
    sys.exit(exit_code)
