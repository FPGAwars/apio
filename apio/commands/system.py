# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO SYSTEM command"""

import click
from apio import util
from apio.util import get_systype
from apio.managers.system import System

# ------------------
# -- CONSTANTS
# ------------------
CMD = "system"  # -- Comand name
LSFTDI = "lsftdi"  # -- Option
LSUSB = "lsusb"  # -- Option
LSSERIAL = "lsserial"  # -- Option
INFO = "info"  # -- Option


@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.option(
    f"--{LSFTDI}", is_flag=True, help="List all connected FTDI devices."
)
@click.option(
    f"--{LSUSB}", is_flag=True, help="List all connected USB devices."
)
@click.option(
    f"--{LSSERIAL}", is_flag=True, help="List all connected Serial devices."
)
@click.option("-i", f"--{INFO}", is_flag=True, help="Show system information.")
def cli(ctx, **kwargs):
    # def cli(ctx, lsftdi, lsusb, lsserial, info):
    """System tools."""

    # -- Extract the arguments
    lsftdi = kwargs[LSFTDI]
    lsusb = kwargs[LSUSB]
    lsserial = kwargs[LSSERIAL]
    info = kwargs[INFO]

    # -- Create the system object
    system = System()

    # -- List all connected ftdi devices
    if lsftdi:
        exit_code = system.lsftdi()

    # -- List all connected USB devices
    elif lsusb:
        exit_code = system.lsusb()

    # -- List all connected serial devices
    elif lsserial:
        exit_code = system.lsserial()

    # -- Show system information
    elif info:
        click.secho("Platform: ", nl=False)
        click.secho(get_systype(), fg="yellow")
        exit_code = 0

    # -- Invalid option. Just show the help
    else:
        click.secho(ctx.get_help())
        exit_code = 0

    # -- Done!
    ctx.exit(exit_code)
