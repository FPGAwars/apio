# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio init' command"""

# pylint: disable=fixme
# TODO: After migrating IceStudio to the create/modify commands, delete
# this command and the *_deprecated methods it call.

from pathlib import Path
import click
from click.core import Context
from apio.managers.project import Project, DEFAULT_TOP_MODULE
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
    help="(Advanced, for developers) Create default SConstruct file.",
    cls=util.ApioOption,
)


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The init command is DEPRECATED and will be deleted in the
future. Use instead the commands 'apio create' and 'apio modify'.
"""


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
@click.command(
    "init",
    short_help="[DEPRECATED] Manage apio projects.",
    help=HELP,
    cls=util.ApioCommand,
)
@click.pass_context
@options.board_option_gen(help="Create init file with the selected board.")
@options.top_module_option_gen(help="Set the top_module in the init file")
@options.project_dir_option
@options.sayyes
@scons_option
def cli(
    ctx: Context,
    # Options
    board: str,
    top_module: str,
    project_dir: Path,
    sayyes: bool,
    scons: bool,
):
    # def cli(ctx, board, top_module, scons, project_dir, sayyes):
    """[deprecated] Manage apio projects."""

    # -- Create a project
    project = Project(project_dir)

    # -- scons option: Create default SConstruct file
    if scons:
        project.create_sconstruct_deprecated("ice40", sayyes)

    # -- Create the project file apio.ini
    elif board:
        # -- Set the default top_module when creating the ini file
        if not top_module:
            top_module = DEFAULT_TOP_MODULE

        # -- Create the apio.ini file
        project.create_ini_deprecated(board, top_module, sayyes)

    # -- Add the top_module to the apio.ini file
    elif top_module:

        # -- Update the apio.ini file
        project.update_ini_deprecated(top_module)

    # -- No options: show help
    else:
        click.secho(ctx.get_help())
