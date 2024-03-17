# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO DRIVERS command"""

import click
from apio.managers.drivers import Drivers
from apio import util

# ------------------
# -- CONSTANTS
# ------------------
CMD = "drivers"  # -- Comand name
FTDI_ENABLE = "ftdi_enable"  # -- Option
FTDI_DISABLE = "ftdi_disable"  # -- Option
SERIAL_ENABLE = "serial_enable"  # -- Option
SERIAL_DISABLE = "serial_disable"  # -- Option


@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.option("--ftdi-enable", is_flag=True, help="Enable FTDI drivers.")
@click.option("--ftdi-disable", is_flag=True, help="Disable FTDI drivers.")
@click.option("--serial-enable", is_flag=True, help="Enable Serial drivers.")
@click.option("--serial-disable", is_flag=True, help="Disable Serial drivers.")
def cli(ctx, **kwargs):
    """Manage FPGA boards drivers."""

    # -- Extract the arguments
    ftdi_enable = kwargs[FTDI_ENABLE]
    ftdi_disable = kwargs[FTDI_DISABLE]
    serial_enable = kwargs[SERIAL_ENABLE]
    serial_disable = kwargs[SERIAL_DISABLE]

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
