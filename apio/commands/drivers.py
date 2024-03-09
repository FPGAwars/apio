# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Main implementation of APIO DRIVERS command"""

import click

from apio.managers.drivers import Drivers
from apio import util


@click.command("drivers", context_settings=util.context_settings())
@click.pass_context
@click.option("--ftdi-enable", is_flag=True, help="Enable FTDI drivers.")
@click.option("--ftdi-disable", is_flag=True, help="Disable FTDI drivers.")
@click.option("--serial-enable", is_flag=True, help="Enable Serial drivers.")
@click.option("--serial-disable", is_flag=True, help="Disable Serial drivers.")
def cli(
    ctx,
    ftdi_enable: bool,
    ftdi_disable: bool,
    serial_enable: bool,
    serial_disable: bool,
):
    """Manage FPGA boards drivers."""

    # -- Default exit code
    exit_code = 0

    # -- Access to the Drivers
    drivers = Drivers()

    # -- FTDI enable option
    if ftdi_enable:
        exit_code = drivers.ftdi_enable()

    elif ftdi_disable:
        exit_code = Drivers().ftdi_disable()
    elif serial_enable:  # pragma: no cover
        exit_code = Drivers().serial_enable()
    elif serial_disable:  # pragma: no cover
        exit_code = Drivers().serial_disable()
    else:
        click.secho(ctx.get_help())

    ctx.exit(exit_code)
