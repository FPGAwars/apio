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

    # -- Access to the Drivers
    drivers = Drivers()

    # -- FTDI enable option
    if ftdi_enable:
        exit_code = drivers.ftdi_enable()

    # -- FTDI disable option
    elif ftdi_disable:
        exit_code = drivers.ftdi_disable()

    # -- Serial enable option
    elif serial_enable:
        exit_code = drivers.serial_enable()

    # -- Serial disable option
    elif serial_disable:
        exit_code = drivers.serial_disable()

    # -- No options. Show the help
    else:
        exit_code = 0
        click.secho(ctx.get_help())

    # -- Return exit code
    ctx.exit(exit_code)
