# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.drivers import Drivers


@click.command('drivers')
@click.pass_context
@click.option('--ftdi-enable', is_flag=True,
              help='Enable FTDI drivers.')
@click.option('--ftdi-disable', is_flag=True,
              help='Disable FTDI drivers.')
@click.option('--serial-enable', is_flag=True,
              help='Enable Serial drivers.')
@click.option('--serial-disable', is_flag=True,
              help='Disable Serial drivers.')
def cli(ctx, ftdi_enable, ftdi_disable, serial_enable, serial_disable):
    """Manage FPGA boards drivers."""

    exit_code = 0

    if ftdi_enable:   # pragma: no cover
        exit_code = Drivers().ftdi_enable()
    elif ftdi_disable:   # pragma: no cover
        exit_code = Drivers().ftdi_disable()
    elif serial_enable:   # pragma: no cover
        exit_code = Drivers().serial_enable()
    elif serial_disable:   # pragma: no cover
        exit_code = Drivers().serial_disable()
    else:
        click.secho(ctx.get_help())

    ctx.exit(exit_code)
