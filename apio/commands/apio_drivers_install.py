# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio drivers install' command"""

import sys
import click
from apio.managers.drivers import Drivers
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils.cmd_util import ApioGroup, ApioSubgroup


# -- apio drivers install ftdi

APIO_DRIVERS_INSTALL_FTDI_HELP = """
The command 'apio drivers install ftdi' installs on your system the FTDI
drivers required by some FPGA boards.

\b
Examples:
  apio drivers install ftdi     # Install the ftdi drivers.
"""


@click.command(
    name="ftdi",
    short_help="Install the ftdi drivers.",
    help=APIO_DRIVERS_INSTALL_FTDI_HELP,
)
def _ftdi_cli():
    """Implements the 'apio drivers install ftdi' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # -- Install.
    exit_code = drivers.ftdi_install()
    sys.exit(exit_code)


# -- apio driver install serial

APIO_DRIVERS_INSTALL_SERIAL_HELP = """
The command ‘apio drivers install serial’ installs the necessary serial
drivers on your system, as required by certain FPGA boards.

\b
Examples:
  apio drivers install serial    # Install the serial drivers.
"""


@click.command(
    name="serial",
    short_help="Install the serial drivers.",
    help=APIO_DRIVERS_INSTALL_SERIAL_HELP,
)
def _serial_cli():
    """Implements the 'apio drivers install serial' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # Insall
    exit_code = drivers.serial_install()
    sys.exit(exit_code)


# --- apio drivers install

# -- Text in the markdown format of the python rich library.
APIO_DRIVERS_INSTALL_HELP = """
The command group 'apio drivers install' includes subcommands that that \
install system drivers that are used to upload designs to FPGA boards.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _ftdi_cli,
            _serial_cli,
        ],
    )
]


@click.command(
    name="install",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Install drivers.",
    help=APIO_DRIVERS_INSTALL_HELP,
)
def cli():
    """Implements the 'apio drivers install' command."""

    # pass
