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

# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
frdi_enable_option = click.option(
    "ftdi_enable",  # Var name.
    "--ftdi-enable",
    is_flag=True,
    help="Enable FTDI drivers.",
)

ftdi_disable_option = click.option(
    "ftdi_disable",  # Var name.
    "--ftdi-disable",
    is_flag=True,
    help="Disable FTDI drivers.",
)

serial_enable_option = click.option(
    "serial_enable",  # Var name.
    "--serial-enable",
    is_flag=True,
    help="Enable Serial drivers.",
)

serial_disable_option = click.option(
    "serial_disable",  # Var name.
    "--serial-disable",
    is_flag=True,
    help="Disable Serial drivers.",
)


# ---------------------------
# -- COMMAND
# ---------------------------
@click.command("drivers", context_settings=util.context_settings())
@click.pass_context
@frdi_enable_option
@ftdi_disable_option
@serial_enable_option
@serial_disable_option
def cli(
    ctx,
    # Options:
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
