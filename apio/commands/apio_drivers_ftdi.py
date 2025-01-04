# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio drivers ftdi' command"""

import sys
import click
from apio.managers.drivers import Drivers
from apio.apio_context import ApioContext, ApioContextScope
from apio.cmd_util import ApioGroup, ApioSubgroup
from apio.managers.system import System


# -- apio drivers ftdi install

APIO_DRIVERS_FTDI_INSTALL_HELP = """
The command 'apio drivers ftdi install' installs on your system the FTDI
drivers required by some FPGA boards.

\b
Examples:
  apio drivers ftdi install      # Install the ftdi drivers.
  apio drivers ftdi uinstall     # Uinstall the ftdi drivers.
"""


@click.command(
    name="install",
    short_help="Install the ftdi drivers.",
    help=APIO_DRIVERS_FTDI_INSTALL_HELP,
)
def _install_cli():
    """Implements the 'apio drivers ftdi install' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # # -- FTDI install option
    # if ftdi_install:
    exit_code = drivers.ftdi_install()
    sys.exit(exit_code)


# -- apio driver ftdi uninstall

APIO_DRIVERS_FTDI_UNINSTALL_HELP = """
The command 'apio drivers ftdi uninstall' removes the FTDI drivers that may
have been installed earlier.

\b
Examples:
  apio drivers ftdi install      # Install the ftdi drivers.
  apio drivers ftdi uinstall     # Uinstall the ftdi drivers.

"""


@click.command(
    name="uninstall",
    short_help="Uninstall the ftdi drivers.",
    help=APIO_DRIVERS_FTDI_UNINSTALL_HELP,
)
def _uninstall_cli():
    """Implements the 'apio drivers ftdi uninstall' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # -- Uninstall
    exit_code = drivers.ftdi_uninstall()
    sys.exit(exit_code)


# -- apio drivers ftdi list


APIO_DRIVERS_FTDI_LIST_HELP = """
The command 'apio drivers ftdi list' displays the FTDI devices currently
connected to your computer. It is useful for diagnosing FPGA board
connectivity issues.

\b
Examples:
  apio drivers ftdi list     # List the ftdi devices.

[Hint] This command uses the lsftdi utility, which can also be invoked
directly with the 'apio raw -- lsftdi <flags>' command.
"""


@click.command(
    name="list",
    short_help="List the connected ftdi devices.",
    help=APIO_DRIVERS_FTDI_LIST_HELP,
)
def _list_cli():
    """Implements the 'apio drivers ftdi list' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Create the system object
    system = System(apio_ctx)

    # -- List all connected ftdi devices
    exit_code = system.lsftdi()
    sys.exit(exit_code)


# --- apio drivers ftdi

APIO_DRIVERS_FTDI_HELP = """
The command group 'apio drivers ftdi' includes subcommands that help manage
the FTDI drivers on your system.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _install_cli,
            _uninstall_cli,
            _list_cli,
        ],
    )
]


@click.command(
    name="ftdi",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Manage the ftdi drivers.",
    help=APIO_DRIVERS_FTDI_HELP,
)
def cli():
    """Implements the 'apio drivers ftdi' command."""

    # pass
