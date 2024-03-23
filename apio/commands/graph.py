# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO GRAPH command"""

from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import util

# ------------------
# -- CONSTANTS
# ------------------
CMD = "graph"  # -- Comand name
PROJECT_DIR = "project_dir"  # -- Option
TOP_MODULE = "top_module"  # -- Option
VERBOSE = "verbose"  # -- Option


@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-p",
    "--project-dir",
    type=Path,
    metavar="path",
    help="Set the target directory for the project.",
)
@click.option(
    "-v",
    f"--{VERBOSE}",
    is_flag=True,
    help="Show the entire output of the command.",
)
@click.option(
    "--top-module",
    type=str,
    metavar="top_module",
    help="Set the top level module (w/o .v ending) to graph.",
)
def cli(ctx, **kwargs):
    """Generate a a visual graph of the verilog code."""

    # -- Extract the arguments
    project_dir = kwargs[PROJECT_DIR]
    verbose = kwargs[VERBOSE]
    top_module = kwargs[TOP_MODULE]

    # -- Crete the scons object
    scons = SCons(project_dir)

    # -- Graph the project with the given parameters
    exit_code = scons.graph(
        {
            "verbose": {"all": verbose, "yosys": False, "pnr": False},
            "top-module": top_module,
        }
    )

    # -- Done!
    ctx.exit(exit_code)
