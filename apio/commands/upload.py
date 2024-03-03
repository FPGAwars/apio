# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Implement the apio upload command"""

import click

from apio.managers.scons import SCons
from apio.managers.drivers import Drivers
from apio import util


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
# R0914: Too many local variables (16/15) (too-many-locals)
# pylint: disable=R0914
@click.command("upload", context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-b", "--board", type=str, metavar="board", help="Set the board."
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
@click.option("-s", "--sram", is_flag=True, help="Perform SRAM programming.")
@click.option("-f", "--flash", is_flag=True, help="Perform FLASH programming.")
@click.option(
    "-p",
    "--project-dir",
    type=str,
    metavar="path",
    help="Set the target directory for the project.",
)
@click.option(
    "-v",
    "--verbose",
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
def cli(
    ctx,
    board: str,  # -- Board name
    serial_port: str,  # -- Serial port name
    ftdi_id: str,  # -- ftdi id
    sram: bool,  # -- Perform SRAM programming
    flash: bool,  # -- Perform Flash programming
    project_dir,
    verbose,
    verbose_yosys,
    verbose_pnr,
    top_module,
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
