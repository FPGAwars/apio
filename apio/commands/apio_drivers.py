# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio drivers' command group."""

import sys
import click
from apio.cmd_util import ApioGroup, ApioSubgroup
from apio.commands import apio_drivers_ftdi, apio_drivers_serial
from apio.apio_context import ApioContext, ApioContextScope
from apio.managers.system import System

# --- apio drivers lsusb

APIO_DRIVERS_LSUSB_HELP = """
The command ‘apio drivers lsusb’ runs the lsusb utility to list the USB
devices connected to your computer. It is typically used for diagnosing
connectivity issues with FPGA boards.

\b
Examples:
  apio drivers lsusb      # List the usb devices

[Hint] You can also run the lsusb utility using the command
'apio raw -- lsusb <flags>'.
"""


@click.command(
    name="lsusb",
    short_help="List connected USB devices.",
    help=APIO_DRIVERS_LSUSB_HELP,
)
def _lsusb_cli():
    """Implements the 'apio driverss lsusb' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Create the system object
    system = System(apio_ctx)

    # -- List the USB device.
    exit_code = system.lsusb()
    sys.exit(exit_code)


# --- apio drivers

APIO_DRIVERS_HELP = """
The command group ‘apio drivers’ contains subcommands to manage the
drivers on your system.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            apio_drivers_ftdi.cli,
            apio_drivers_serial.cli,
            _lsusb_cli,
        ],
    )
]


@click.command(
    name="drivers",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Manage the operating system drivers.",
    help=APIO_DRIVERS_HELP,
)
def cli():
    """Implements the drivers command."""

    # pass
