# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio upload' command"""

from pathlib import Path
import click
from click.core import Context
from apio.managers.scons import SCons
from apio.managers.drivers import Drivers
from apio import cmd_util
from apio.commands import options
from apio.resources import Resources


# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
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

HELP = """
The uploade command builds the bitstream file (similar to the
build command) and uploaded it to the FPGA board.
The commands is typically used in the root directory
of the project that contains the apio.ini file.

\b
Examples:
  apio upload
"""


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
@click.command(
    "upload",
    short_help="Upload the bitstream to the FPGA.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.project_dir_option
@options.serial_port_option
@options.ftdi_id
@sram_option
@flash_option
@options.verbose_option
@options.verbose_yosys_option
@options.verbose_pnr_option
@options.top_module_option_gen(deprecated=True)
@options.board_option_gen(deprecated=True)
def cli(
    ctx: Context,
    # Options
    project_dir: Path,
    serial_port: str,
    ftdi_id: str,
    sram: bool,
    flash: bool,
    verbose: bool,
    verbose_yosys: bool,
    verbose_pnr: bool,
    # Deprecated options
    top_module: str,
    board: str,
):
    """Implements the upload command."""

    # -- Create a drivers object
    resources = Resources(project_dir=project_dir, project_scope=True)
    drivers = Drivers(resources)

    # -- Only for MAC
    # -- Operation to do before uploading a design in MAC
    drivers.pre_upload()

    # -- Create the SCons object
    scons = SCons(resources)

    # -- Construct the configuration params to pass to SCons
    # -- from the arguments
    config = {
        "board": board,
        "verbose": {
            "all": verbose,
            "yosys": verbose_yosys,
            "pnr": verbose_pnr,
        },
        "top-module": top_module,
    }

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
    ctx.exit(exit_code)


# Advanced notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-upload
