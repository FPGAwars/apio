# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2017 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.drivers import Drivers


@click.command('drivers')
@click.pass_context
@click.option('-e', '--enable', is_flag=True,
              help='Enable FPGA drivers.')
@click.option('-d', '--disable', is_flag=True,
              help='Disable FPGA drivers.')
def cli(ctx, enable, disable):
    """Manage FPGA drivers."""

    exit_code = 0

    if enable:   # pragma: no cover
        exit_code = Drivers().enable()
    elif disable:   # pragma: no cover
        exit_code = Drivers().disable()
    else:
        click.secho(ctx.get_help())

    ctx.exit(exit_code)
