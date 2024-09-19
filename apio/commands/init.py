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
from click.core import Context
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
    help="(Advanced, for developers) Create default SConstruct file.",
)


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
[Note] This command is DEPRECATED. To create a new project use the
examples command and fetch an example of your FPGA board.
To modify the configuration of an existing project, edit its
apio.ini file manually.

[Developers] To develope an SConstruct file either symlink the
pip apio package to the apio directory of your dev directory
(recommanded), or copy SConstruct to the project dir and it will
be fetched from there (make sure copy the correct SConstruct file for
your FPGA board)

The command is preserved for now to backward compatibility and
may be eliminated in a future release.
"""


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
@click.command(
    "init",
    short_help="(deprecated) Manage apio projects.",
    help=HELP,
    context_settings=util.context_settings(),
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
