# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO INIT command"""

from pathlib import Path
import click
from apio.managers.project import Project
from apio import util

# ------------------
# -- CONSTANTS
# ------------------
CMD = "init"  # -- Comand name
BOARD = "board"  # -- Option
SCONS = "scons"  # -- Option
PROJECT_DIR = "project_dir"  # -- Option
SAYYES = "sayyes"  # -- Option
TOP_MODULE = "top_module"  # -- Option


@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-b",
    f"--{BOARD}",
    type=str,
    metavar="str",
    help="Create init file with the selected board.",
)
@click.option(
    "-t",
    "--top-module",
    type=str,
    metavar="top_module",
    help="Set the top_module in the init file",
)
@click.option(
    "-s", f"--{SCONS}", is_flag=True, help="Create default SConstruct file."
)
@click.option(
    "-p",
    "--project-dir",
    type=Path,
    metavar="project_dir",
    help="Set the target directory for the project.",
)
@click.option(
    "-y",
    f"--{SAYYES}",
    is_flag=True,
    help="Automatically answer YES to all the questions.",
)
def cli(ctx, **kwargs):
    # def cli(ctx, board, top_module, scons, project_dir, sayyes):
    """Manage apio projects."""

    # -- Extract the arguments
    project_dir = kwargs[PROJECT_DIR]
    scons = kwargs[SCONS]
    board = kwargs[BOARD]
    sayyes = kwargs[SAYYES]
    top_module = kwargs[TOP_MODULE]

    # -- Create a project
    project = Project()

    # -- scons option: Create default SConstruct file
    if scons:
        project.create_sconstruct(project_dir, "ice40", sayyes)

    # -- Create the apio.ini file
    elif board:
        # -- Set the default top_module when creating the ini file
        if not top_module:
            top_module = "main"

        # -- Create the apio.ini file
        project.create_ini(board, top_module, project_dir, sayyes)

    # -- Add the top_module to the apio.ini file
    elif top_module:

        # -- Update the apio.ini file
        project.update_ini(top_module, project_dir)

    # -- No options: show help
    else:
        click.secho(ctx.get_help())
