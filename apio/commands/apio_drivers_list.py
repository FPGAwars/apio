# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio drivers list' command"""

import sys
import click
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils.cmd_util import ApioGroup, ApioSubgroup
from apio.managers.system import System


# -- apio drivers list ftdi


APIO_DRIVERS_LIST_FTDI_HELP = """
The command 'apio drivers list ftdi' displays the FTDI devices currently
connected to your computer. It is useful for diagnosing FPGA board
connectivity issues.

\b
Examples:
  apio drivers list ftdi     # List the ftdi devices.

[Hint] This command uses the lsftdi utility, which can also be invoked
directly with the 'apio raw -- lsftdi <flags>' command.
"""


@click.command(
    name="ftdi",
    short_help="List the connected ftdi devices.",
    help=APIO_DRIVERS_LIST_FTDI_HELP,
)
def _ftdi_cli():
    """Implements the 'apio drivers list ftdi' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Create the system object
    system = System(apio_ctx)

    # -- List all connected ftdi devices
    exit_code = system.lsftdi()
    sys.exit(exit_code)


# -- apio drivers list serial

APIO_DRIVERS_LIST_SERIAL_HELP = """
The command ‘apio drivers list serial’ lists the serial devices connected to
your computer. It is useful for diagnosing FPGA board connectivity issues.

\b
Examples:
  apio drivers list serial    # List the serial devices.

[Hint] This command executes the utility lsserial, which can also be invoked
using the command 'apio raw -- lsserial <flags>'.
"""


@click.command(
    name="serial",
    short_help="List the connected serial devices.",
    help=APIO_DRIVERS_LIST_SERIAL_HELP,
)
def _serial_cli():
    """Implements the 'apio drivers list serial' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Create the system object
    system = System(apio_ctx)

    # # -- List all connected serial devices
    exit_code = system.lsserial()
    sys.exit(exit_code)


# --- apio drivers list usb

APIO_DRIVERS_LIST_USB_HELP = """
The command ‘apio drivers list usb runs the lsusb utility to list the USB
devices connected to your computer. It is typically used for diagnosing
connectivity issues with FPGA boards.

\b
Examples:
  apio drivers list usb      # List the usb devices

[Hint] You can also run the lsusb utility using the command
'apio raw -- lsusb <flags>'.
"""


@click.command(
    name="usb",
    short_help="List connected USB devices.",
    help=APIO_DRIVERS_LIST_USB_HELP,
)
def _usb_cli():
    """Implements the 'apio driverss list usb' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Create the system object
    system = System(apio_ctx)

    # -- List the USB device.
    exit_code = system.lsusb()
    sys.exit(exit_code)


# --- apio drivers list

# -- Text in the markdown format of the python rich library.
APIO_DRIVERS_LIST_HELP = """
The command group 'apio drivers list' includes subcommands that that lists \
system drivers that are used with FPGA boards.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _ftdi_cli,
            _serial_cli,
            _usb_cli,
        ],
    )
]


@click.command(
    name="list",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="List system drivers.",
    help=APIO_DRIVERS_LIST_HELP,
)
def cli():
    """Implements the 'apio drivers list' command."""

    # pass
