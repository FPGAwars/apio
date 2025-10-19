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
from apio.managers.scons_manager import SConsManager
from apio.utils import cmd_util
from apio.commands import options
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.managers.programmers import construct_programmer_cmd
from apio.common.proto.apio_pb2 import UploadParams


# --------- apio upload

serial_port_option = click.option(
    "serial_port",  # Var name.
    "-s",
    "--serial-port",
    type=str,
    metavar="serial-port",
    help="Set the serial port.",
    cls=cmd_util.ApioOption,
)

serial_num_option = click.option(
    "serial_num",  # Var name.
    "-n",
    "--serial-num",
    type=str,
    metavar="serial-num",
    help="Select the device's USB serial number.",
    cls=cmd_util.ApioOption,
)


# -- Text in the rich-text format of the python rich library.
APIO_UPLOAD_HELP = """
The command 'apio upload' builds the bitstream file (similar to the \
'apio build' command) and uploads it to the FPGA board.

Examples:[code]
  apio upload                            # Typical invocation
  apio upload -s /dev/cu.usbserial-1300  # Select serial port
  apio upload -n FTXYA34Z                # Select serial number[/code]

Typically the simple form 'apio upload' is sufficient to locate and program \
the FPGA board. The optional flags '--serial-port' and '--serial-num' allows \
to select the desired board if more than one matching board is detected.

[HINT] You can use the command 'apio devices' to list the connected USB and \
serial devices and the command 'apio drivers' to install and uninstall device \
drivers.

[HINT] The default programmer command of your board can be overridden using \
the apio.ini option 'programmer-cmd'.
"""


@click.command(
    name="upload",
    cls=cmd_util.ApioCommand,
    short_help="Upload the bitstream to the FPGA.",
    help=APIO_UPLOAD_HELP,
)
@click.pass_context
@serial_port_option
@serial_num_option
@options.env_option_gen()
@options.project_dir_option
def cli(
    _: click.Context,
    # Options
    serial_port: str,
    serial_num: str,
    env: Optional[str],
    project_dir: Optional[Path],
):
    """Implements the upload command."""

    # -- Create a apio context.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.PROJECT_REQUIRED,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        project_dir_arg=project_dir,
        env_arg=env,
    )

    # -- Set the shell env.
    apio_ctx.set_env_for_packages()

    # -- Get the programmer command.
    programmer_cmd = construct_programmer_cmd(
        apio_ctx, serial_port_flag=serial_port, serial_num_flag=serial_num
    )

    # Construct the scons upload params.
    upload_params = UploadParams(programmer_cmd=programmer_cmd)

    # -- Create the scons manager
    scons = SConsManager(apio_ctx)

    # Run scons: upload command
    exit_code = scons.upload(upload_params)

    # -- Done!
    sys.exit(exit_code)


# Advanced notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-upload
