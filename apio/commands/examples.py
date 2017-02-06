# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2017 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.examples import Examples

# Python3 compat
import sys
if (sys.version_info > (3, 0)):
    unicode = str


@click.command('examples')
@click.pass_context
@click.option('-l', '--list', is_flag=True,
              help='List all available examples.')
@click.option('-d', '--dir', type=unicode, metavar='name',
              help='Copy the selected example directory.')
@click.option('-f', '--files', type=unicode, metavar='name',
              help='Copy the selected example files.')
@click.option('-p', '--project-dir', type=unicode, metavar='path',
              help='Set the target directory for the examples.')
@click.option('-n', '--sayno', is_flag=True,
              help='Automatically answer NO to all the questions.')
def cli(ctx, list, dir, files, project_dir, sayno):
    """Manage verilog examples.\n
       Install with `apio install examples`"""

    exit_code = 0

    if list:
        exit_code = Examples().list_examples()
    elif dir:
        exit_code = Examples().copy_example_dir(dir, project_dir, sayno)
    elif files:
        exit_code = Examples().copy_example_files(files, project_dir, sayno)
    else:
        click.secho(ctx.get_help())
        click.secho(Examples().examples_of_use_cad())

    ctx.exit(exit_code)
