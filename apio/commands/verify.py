# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO VERIFY command"""

from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import util

# ------------------
# -- CONSTANTS
# ------------------
CMD = "verify"  # -- Comand name
BOARD = "board"  # -- Option
VERBOSE = "verbose"  # -- Option
PROJECT_DIR = "project_dir"  # -- Option


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
    "-b", f"--{BOARD}", type=str, metavar="board", help="Set the board."
)
@click.option(
    "-v",
    f"--{VERBOSE}",
    is_flag=True,
    help="Show the entire output of the command.",
)
def cli(ctx, **kwargs):
    """Verify the verilog code."""

    # -- Extract the arguments
    project_dir = kwargs[PROJECT_DIR]
    board = kwargs[BOARD]
    verbose = kwargs[VERBOSE]

    # -- Crete the scons object
    scons = SCons(project_dir)

    # -- Verify the project with the given parameters
    exit_code = scons.verify(
        {
            "board": board,
            "verbose": {"all": verbose, "yosys": False, "pnr": False},
        }
    )

    # -- Done!
    ctx.exit(exit_code)
