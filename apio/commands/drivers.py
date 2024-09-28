# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio drivers' command"""

from varname import nameof
import click
from click.core import Context
from apio.managers.drivers import Drivers
from apio import cmd_util

# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
frdi_enable_option = click.option(
    "ftdi_enable",  # Var name.
    "--ftdi-enable",
    is_flag=True,
    help="Enable FTDI drivers.",
    cls=cmd_util.ApioOption,
)

ftdi_disable_option = click.option(
    "ftdi_disable",  # Var name.
    "--ftdi-disable",
    is_flag=True,
    help="Disable FTDI drivers.",
    cls=cmd_util.ApioOption,
)

serial_enable_option = click.option(
    "serial_enable",  # Var name.
    "--serial-enable",
    is_flag=True,
    help="Enable Serial drivers.",
    cls=cmd_util.ApioOption,
)

serial_disable_option = click.option(
    "serial_disable",  # Var name.
    "--serial-disable",
    is_flag=True,
    help="Disable Serial drivers.",
    cls=cmd_util.ApioOption,
)


# ---------------------------
# -- COMMAND
# ---------------------------

HELP = """
The drivers command allows to install or uninstall operating system
drivers that are used to program the FPGA boards. This command is global
and affects all the projects on the local host.

\b
Examples:
  apio drivers --ftdi-enable     # Install FTDI driver
  apio drivers --ftdi-disable    # Uninstall FTDI driver
  apio drivers --serial-enable   # Install serial driver
  apio drivers --serial-disable  # Uninstall serial driver

  Do not specify more than flag per command invocation.
"""


@click.command(
    "drivers",
    short_help="Manage the operating system drivers.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@frdi_enable_option
@ftdi_disable_option
@serial_enable_option
@serial_disable_option
def cli(
    ctx: Context,
    # Options:
    ftdi_enable: bool,
    ftdi_disable: bool,
    serial_enable: bool,
    serial_disable: bool,
):
    """Implements the drivers command."""

    # Make sure these params are exclusive.
    cmd_util.check_exclusive_params(
        ctx, nameof(ftdi_enable, ftdi_disable, serial_enable, serial_disable)
    )

    # -- Access to the Drivers
    drivers = Drivers()

    # -- FTDI enable option
    if ftdi_enable:
        exit_code = drivers.ftdi_enable()
        ctx.exit(exit_code)

    # -- FTDI disable option
    if ftdi_disable:
        exit_code = drivers.ftdi_disable()
        ctx.exit(exit_code)

    # -- Serial enable option
    if serial_enable:
        exit_code = drivers.serial_enable()
        ctx.exit(exit_code)

    # -- Serial disable option
    if serial_disable:
        exit_code = drivers.serial_disable()
        ctx.exit(exit_code)

    # -- No options. Show the help
    click.secho(ctx.get_help())
