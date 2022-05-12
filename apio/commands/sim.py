# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""TODO"""

import click
from apio.managers.scons import SCons


@click.command("sim")
@click.pass_context
@click.option(
    "-p",
    "--project-dir",
    type=str,
    metavar="path",
    help="Set the target directory for the project.",
)
def cli(ctx, project_dir):
    """Launch the verilog simulation."""

    exit_code = SCons(project_dir).sim()
    ctx.exit(exit_code)
