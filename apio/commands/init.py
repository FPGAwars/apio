# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2017 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.project import Project

# Python3 compat
import sys
if (sys.version_info > (3, 0)):
    unicode = str


@click.command('init')
@click.pass_context
@click.option('-s', '--scons', is_flag=True,
              help='Create default SConstruct file.')
@click.option('-b', '--board', type=unicode, metavar='board',
              help='Create init file with the selected board.')
@click.option('-p', '--project-dir', type=unicode, metavar='path',
              help='Set the target directory for the project.')
@click.option('-y', '--sayyes', is_flag=True,
              help='Automatically answer YES to all the questions.')
def cli(ctx, board, scons, project_dir, sayyes):
    """Manage apio projects."""

    if scons:
        Project().create_sconstruct(project_dir, sayyes)
    elif board:
        Project().create_ini(board, project_dir, sayyes)
    else:
        click.secho(ctx.get_help())
