# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio drivers uninstall' command"""

import sys
import click
from apio.managers.drivers import Drivers
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils.cmd_util import ApioGroup, ApioSubgroup


# -- apio driver uninstall ftdi

APIO_DRIVERS_UNINSTALL_FTDI_HELP = """
The command 'apio drivers uninstall ftdi' removes the FTDI drivers that may
have been installed earlier.

\b
Examples:
  apio drivers uninstall ftdi     # Uninstall the ftdi drivers.

"""


@click.command(
    name="ftdi",
    short_help="Uninstall the ftdi drivers.",
    help=APIO_DRIVERS_UNINSTALL_FTDI_HELP,
)
def _ftdi_cli():
    """Implements the 'apio drivers uninstall ftdi' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # -- Uninstall
    exit_code = drivers.ftdi_uninstall()
    sys.exit(exit_code)


# -- apio drivers uninstall serial

APIO_DRIVERS_UNINSTALL_SERIAL_HELP = """
The command ‘apio drivers uninstall serial’ removes the serial drivers that
you may have installed earlier.

\b
Examples:
  apio drivers uinstall serial    # Uinstall the serial drivers.
"""


@click.command(
    name="serial",
    short_help="Uninstall the serial drivers.",
    help=APIO_DRIVERS_UNINSTALL_SERIAL_HELP,
)
def _serial_cli():
    """Implements the 'apio drivers uninstall serial' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # -- Uninstall
    exit_code = drivers.serial_uninstall()
    sys.exit(exit_code)


# --- apio drivers uninstall

# -- Text in the markdown format of the python rich library.
APIO_DRIVERS_UNINSTALL_HELP = """
The command group 'apio drivers uninstall' includes subcommands that that \
uninstall system drivers that are used to upload designs to FPGA boards.
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
    name="uninstall",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Uninstall drivers.",
    help=APIO_DRIVERS_UNINSTALL_HELP,
)
def cli():
    """Implements the 'apio drivers uninstall' command."""

    # pass
