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


@click.command("sim", context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-p",
    "--project-dir",
    type=Path,
    metavar="path",
    help="Set the target directory for the project.",
)
@click.option(
    "-t",
    "--testbench",
    type=str,
    metavar="testbench",
    help="Specify the testbench file to simulate.",
)
def cli(ctx, project_dir, testbench):
    """Launch the verilog simulation."""

    # -- Create the scons object
    scons = SCons(project_dir)

    # -- Simulate the project with the given parameters
    exit_code = scons.sim({"testbench": testbench})

    # -- Done!
    ctx.exit(exit_code)
