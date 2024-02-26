# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""TODO"""

import click

from apio.managers.scons import SCons
from apio import util


@click.command("graph", context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-p",
    "--project-dir",
    type=str,
    metavar="path",
    help="Set the target directory for the project.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show the entire output of the command.",
)
@click.option(
    "--top-module",
    type=str,
    metavar="top_module",
    help="Set the top level module (w/o .v ending) to graph.",
)
def cli(ctx, project_dir, verbose, top_module):
    """Generate a a visual graph of the verilog code."""

    # -- Crete the scons object
    scons = SCons(project_dir)

    # -- Graph the project with the given parameters
    exit_code = scons.graph(
        {
            "verbose": {"all": verbose, "yosys": False, "pnr": False},
            "top-module": top_module
        }
    )

    # -- Done!
    ctx.exit(exit_code)
