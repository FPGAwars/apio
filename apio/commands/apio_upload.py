# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio upload' command"""

import sys
from typing import Optional
from pathlib import Path
import click
from apio.managers.scons import SCons
from apio.utils import cmd_util
from apio.commands import options
from apio.apio_context import ApioContext, ApioContextScope
from apio.managers.programmers import construct_programmer_cmd
from apio.common.proto.apio_pb2 import UploadParams


# --------- apio upload

serial_port_option = click.option(
    "serial_port",  # Var name.
    "--serial-port",
    type=str,
    metavar="serial-port",
    help="Set the serial port.",
    cls=cmd_util.ApioOption,
)

ftdi_idx_option = click.option(
    "ftdi_idx",  # Var name.
    "--ftdi-idx",
    type=int,
    default=None,  # 0 is a valid value.
    metavar="ftdi-idx",
    help="Consider only FTDI device with given index.",
)


# -- Text in the rich-text format of the python rich library.
APIO_UPLOAD_HELP = """
The command 'apio upload' builds the bitstream file (similar to the \
'apio build' command) and uploads it to the FPGA board.

Examples:[code]
  apio upload              # Typical usage.
  apio upload --ftdi-idx 2 # Consider only FTDI device at index 2[/code]

The optional flag '--ftdi-idx' is used in special cases involving boards with \
FTDI devices, particularly when multiple boards are connected to the host \
computer. It tells Apio to consider only the device at the specified index in \
the list shown by the command: 'apio devices list ftdi'. The first device in \
the list has index 0.

[Note] When apio is installed on Linux using the Snap package \
manager, run the command 'snap connect apio:raw-usb' once \
to grant the necessary permissions to access USB devices.
"""


@click.command(
    name="upload",
    cls=cmd_util.ApioCommand,
    short_help="Upload the bitstream to the FPGA.",
    help=APIO_UPLOAD_HELP,
)
@click.pass_context
@serial_port_option
@ftdi_idx_option
@options.env_option_gen()
@options.project_dir_option
def cli(
    _: click.Context,
    # Options
    serial_port: str,
    ftdi_idx: int,
    env: Optional[str],
    project_dir: Optional[Path],
):
    """Implements the upload command."""

    # -- Create a apio context.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_REQUIRED,
        project_dir_arg=project_dir,
        env_arg=env,
    )

    # -- Create the scons manager
    scons = SCons(apio_ctx)

    # -- Get the programmer command.
    programmer_cmd = construct_programmer_cmd(
        apio_ctx,
        serial_port_arg=serial_port,
        ftdi_idx_arg=ftdi_idx,  # None if not specified.
    )

    # Construct the scons upload params.
    upload_params = UploadParams(programmer_cmd=programmer_cmd)

    # Run scons: upload command
    exit_code = scons.upload(upload_params)

    # -- Done!
    sys.exit(exit_code)


# Advanced notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-upload
