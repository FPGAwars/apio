# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""TODO"""

import click

from apio.managers.project import Project


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
@click.command("init")
@click.pass_context
@click.option(
    "-b",
    "--board",
    type=str,
    metavar="board",
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
    "-s", "--scons", is_flag=True, help="Create default SConstruct file."
)
@click.option(
    "-p",
    "--project-dir",
    type=str,
    metavar="path",
    help="Set the target directory for the project.",
)
@click.option(
    "-y",
    "--sayyes",
    is_flag=True,
    help="Automatically answer YES to all the questions.",
)
def cli(ctx, board, top_module, scons, project_dir, sayyes):
    """Manage apio projects."""

    if scons:
        Project().create_sconstruct(project_dir, "ice40", sayyes)
    elif board:
        # -- Set the default top_module when creating the ini file
        if not top_module:
            top_module = "main"
        Project().create_ini(board, top_module, project_dir, sayyes)
    elif top_module:
        print("INIT TOP-MODULE!!")
        Project().update_ini(top_module)
    else:
        click.secho(ctx.get_help())
