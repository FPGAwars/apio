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

# ------------------
# -- CONSTANTS
# ------------------
CMD = "upload"  # -- Comand name
BOARD = "board"  # -- Option
PROJECT_DIR = "project_dir"  # -- Option
SERIAL_PORT = "serial_port"  # -- Option
FTDI_ID = "ftdi_id"  # -- Option
SRAM = "sram"  # -- Option
FLASH = "flash"  # -- Option
VERBOSE = "verbose"  # -- Option
VERBOSE_YOSYS = "verbose_yosys"  # -- Option
VERBOSE_PNR = "verbose_pnr"  # -- Option
TOP_MODULE = "top_module"  # -- Option


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
# R0914: Too many local variables (16/15) (too-many-locals)
# pylint: disable=R0914
@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-b", f"--{BOARD}", type=str, metavar="board", help="Set the board."
)
@click.option(
    "--serial-port",
    type=str,
    metavar="serial-port",
    help="Set the serial port.",
)
@click.option(
    "--ftdi-id", type=str, metavar="ftdi-id", help="Set the FTDI id."
)
@click.option(
    "-s", f"--{SRAM}", is_flag=True, help="Perform SRAM programming."
)
@click.option(
    "-f", f"--{FLASH}", is_flag=True, help="Perform FLASH programming."
)
@click.option(
    "-p",
    "--project-dir",
    type=Path,
    metavar="path",
    help="Set the target directory for the project.",
)
@click.option(
    "-v",
    f"--{VERBOSE}",
    is_flag=True,
    help="Show the entire output of the command.",
)
@click.option(
    "--verbose-yosys",
    is_flag=True,
    help="Show the yosys output of the command.",
)
@click.option(
    "--verbose-pnr", is_flag=True, help="Show the pnr output of the command."
)
@click.option(
    "--top-module",
    type=str,
    metavar="top_module",
    help="Set the top level module (w/o .v ending) for build.",
)
def cli(ctx, **kwargs):
    # def cli(
    #     ctx,
    #     board: str,  # -- Board name
    #     serial_port: str,  # -- Serial port name
    #     ftdi_id: str,  # -- ftdi id
    #     sram: bool,  # -- Perform SRAM programming
    #     flash: bool,  # -- Perform Flash programming
    #     project_dir,
    #     verbose,
    #     verbose_yosys,
    #     verbose_pnr,
    #     top_module,
    # ):
    """Upload the bitstream to the FPGA."""

    # -- Extract the arguments
    project_dir = kwargs[PROJECT_DIR]
    board = kwargs[BOARD]
    verbose = kwargs[VERBOSE]
    verbose_yosys = kwargs[VERBOSE_YOSYS]
    verbose_pnr = kwargs[VERBOSE_PNR]
    top_module = kwargs[TOP_MODULE]
    serial_port = kwargs[SERIAL_PORT]
    ftdi_id = kwargs[FTDI_ID]
    sram = kwargs[SRAM]
    flash = kwargs[FLASH]

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
