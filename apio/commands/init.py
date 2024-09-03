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
from apio.commands import options


# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
scons_option = click.option(
    "scons",  # Var name.
    "-s",
    "--scons",
    is_flag=True,
    help="Create default SConstruct file.",
)


# ---------------------------
# -- COMMAND
# ---------------------------
# R0913: Too many arguments (6/5)
# pylint: disable=R0913
@click.command("init", context_settings=util.context_settings())
@click.pass_context
@options.board_option_gen(help="Create init file with the selected board.")
@options.top_module_option_gen(help="Set the top_module in the init file")
@scons_option
@options.project_dir_option
@options.sayyes
def cli(
    ctx,
    # Options
    board: str,
    top_module: str,
    scons: bool,
    project_dir: Path,
    sayyes: bool,
):
    # def cli(ctx, board, top_module, scons, project_dir, sayyes):
    """Manage apio projects."""

    # -- Create a project
    project = Project(project_dir)

    # -- scons option: Create default SConstruct file
    if scons:
        project.create_sconstruct("ice40", sayyes)

    # -- Create the project file apio.ini
    elif board:
        # -- Set the default top_module when creating the ini file
        if not top_module:
            top_module = "main"

        # -- Create the apio.ini file
        project.create_ini(board, top_module, sayyes)

    # -- Add the top_module to the apio.ini file
    elif top_module:

        # -- Update the apio.ini file
        project.update_ini(top_module)

    # -- No options: show help
    else:
        click.secho(ctx.get_help())
