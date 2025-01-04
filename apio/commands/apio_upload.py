# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio upload' command"""

import sys
from pathlib import Path
import click
from apio.managers.scons import SCons
from apio.managers.drivers import Drivers
from apio import cmd_util
from apio.commands import options
from apio.apio_context import ApioContext, ApioContextScope


# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
serial_port_option = click.option(
    "serial_port",  # Var name.
    "--serial-port",
    type=str,
    metavar="serial-port",
    help="Set the serial port.",
    cls=cmd_util.ApioOption,
)

ftdi_id_option = click.option(
    "ftdi_id",  # Var name.
    "--ftdi-id",
    type=str,
    metavar="ftdi-id",
    help="Set the FTDI id.",
)

sram_option = click.option(
    "sram",  # Var name.
    "-s",
    "--sram",
    is_flag=True,
    help="Perform SRAM programming.",
    cls=cmd_util.ApioOption,
)

flash_option = click.option(
    "flash",  # Var name.
    "-f",
    "--flash",
    is_flag=True,
    help="Perform FLASH programming.",
    cls=cmd_util.ApioOption,
)


# ---------------------------
# -- COMMAND
# ---------------------------

APIO_UPLOAD_HELP = """
The command ‘apio upload’ builds the bitstream file (similar to the apio build
command) and uploads it to the FPGA board.

\b
Examples:
  apio upload
"""


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
@click.command(
    name="upload",
    short_help="Upload the bitstream to the FPGA.",
    help=APIO_UPLOAD_HELP,
)
@click.pass_context
@serial_port_option
@ftdi_id_option
@sram_option
@flash_option
@options.project_dir_option
def cli(
    _: click.Context,
    # Options
    serial_port: str,
    ftdi_id: str,
    sram: bool,
    flash: bool,
    project_dir: Path,
):
    """Implements the upload command."""

    # -- Create a apio context.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_REQUIRED, project_dir_arg=project_dir
    )

    # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # -- Only for MAC
    # -- Operation to do before uploading a design in MAC
    drivers.pre_upload()

    # -- Create the scons manager
    scons = SCons(apio_ctx)

    # -- Construct the configuration params to pass to SCons
    # -- from the arguments
    config = {}

    # -- Construct the programming configuration
    prog = {
        "serial_port": serial_port,
        "ftdi_id": ftdi_id,
        "sram": sram,
        "flash": flash,
    }

    # Run scons: upload command
    exit_code = scons.upload(config, prog)

    # -- Only for MAC
    # -- Operation to do after uploading a design in MAC
    drivers.post_upload()

    # -- Done!
    sys.exit(exit_code)


# Advanced notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-upload
