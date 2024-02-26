# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""TODO"""

import click
from apio.managers.scons import SCons
from apio import util


@click.command("sim", context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-p",
    "--project-dir",
    type=str,
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

    exit_code = SCons(project_dir).sim({"testbench": testbench})
    ctx.exit(exit_code)
