# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.resources import Resources


@click.command('boards')
@click.pass_context
@click.option('-l', '--list', is_flag=True,
              help='List all supported FPGA boards.')
def cli(ctx, list):
    """Manage FPGA boards."""

    if list:
        Resources().list_boards()
    else:
        click.secho(ctx.get_help())
