# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO CLEAN command"""


from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import util

# ------------------
# -- CONSTANTS
# ------------------
CMD = "clean"  # -- Comand name
BOARD = "board"  # -- Option
PROJECT_DIR = "project_dir"  # -- Option
VERBOSE = "verbose"  # -- Option


@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-p",
    "--project-dir",
    type=Path,
    metavar="str",
    help="Set the target directory for the project.",
)
@click.option(
    "-b", f"--{BOARD}", type=str, metavar="str", help="Set the board."
)
@click.option(
    "-v",
    f"--{VERBOSE}",
    is_flag=True,
    help="Show the entire output of the command.",
)
def cli(ctx, **kwargs):
    """Clean the previous generated files."""

    # -- Extract the arguments
    project_dir = kwargs[PROJECT_DIR]
    board = kwargs[BOARD]
    verbose = kwargs[VERBOSE]

    # -- Create the scons object
    scons = SCons(project_dir)

    # -- Build the project with the given parameters
    exit_code = scons.clean({"board": board, "verbose": {"all": verbose}})

    # -- Done!
    ctx.exit(exit_code)
