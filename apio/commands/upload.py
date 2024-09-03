# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implement the apio upload command"""

from pathlib import Path
import click
from apio.managers.scons import SCons
from apio.managers.drivers import Drivers
from apio import util
from apio.commands import options


# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
sram_option = click.option(
    "sram",  # Var name.
    "-s",
    "--sram",
    is_flag=True,
    help="Perform SRAM programming.",
)

flash_option = click.option(
    "flash",  # Var name.
    "-f",
    "--flash",
    is_flag=True,
    help="Perform FLASH programming.",
)


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
# R0914: Too many local variables (16/15) (too-many-locals)
# pylint: disable=R0914
@click.command("upload", context_settings=util.context_settings())
@click.pass_context
@options.board_option_gen()
@options.serial_port_option
@options.ftdi_id
@sram_option
@flash_option
@options.project_dir_option
@options.verbose_option
@options.verbose_yosys_option
@options.verbose_pnr_option
@options.top_module_option_gen()
def cli(
    ctx,
    # Options
    board: str,
    serial_port: str,
    ftdi_id: str,
    sram: bool,
    flash: bool,
    project_dir: Path,
    verbose: bool,
    verbose_yosys: bool,
    verbose_pnr: bool,
    top_module: str,
):
    """Upload the bitstream to the FPGA."""

    # -- Create a drivers object
    drivers = Drivers()

    # -- Only for MAC
    # -- Operation to do before uploading a design in MAC
    drivers.pre_upload()

    # -- Create the SCons object
    scons = SCons(project_dir)

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
