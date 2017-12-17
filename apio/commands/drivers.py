# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2017 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.drivers import Drivers


@click.command('drivers')
@click.pass_context
@click.option('--ftdi-enable', is_flag=True,
              help='Enable FPGA drivers.')
@click.option('--ftdi-disable', is_flag=True,
              help='Disable FPGA drivers.')
def cli(ctx, ftdi_enable, ftdi_disable):
    """Manage FPGA drivers."""

    exit_code = 0

    if ftdi_enable:   # pragma: no cover
        exit_code = Drivers().enable()
    elif ftdi_disable:   # pragma: no cover
        exit_code = Drivers().disable()
    else:
        click.secho(ctx.get_help())

    ctx.exit(exit_code)
