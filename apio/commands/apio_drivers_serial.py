# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio drivers serial' command"""

import sys
import click
from apio.managers.drivers import Drivers
from apio.managers.system import System
from apio.apio_context import ApioContext
from apio.cmd_util import ApioGroup, ApioSubgroup


# -- apio driver serial install

INSTALL_HELP = """
The command 'apio drivers serial install' installs the serial drivers on your
system as required by some FPGA boards.

\b
Examples:
  apio drivers serial install      # Install the ftdi drivers.
  apio drivers serial uinstall     # Uinstall the ftdi drivers.
"""


@click.command(
    name="install",
    short_help="Install the serial drivers.",
    help=INSTALL_HELP,
)
def _install_cli():
    """Implements the 'apio drivers serial install' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(load_project=False)

    # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # Insall
    exit_code = drivers.serial_install()
    sys.exit(exit_code)


# -- apio drivers serial uninstall

UNINSTALL_HELP = """
The command 'apio drivers serial uninstall' uninstalled the serial drivers that
you may installed eariler. .

\b
Examples:
  apio drivers serial install      # Install the serial drivers.
  apio drivers serial uinstall     # Uinstall the serial drivers.

"""


@click.command(
    name="uninstall",
    short_help="Uninstall the serial drivers.",
    help=UNINSTALL_HELP,
)
def _uninstall_cli():
    """Implements the 'apio drivers serial uninstall' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(load_project=False)

    # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # -- Uninstall
    exit_code = drivers.serial_uninstall()
    sys.exit(exit_code)


# -- apio drivers serial list

LIST_HELP = """
The command 'apio drivers serial list' lists the serial devices connected
to your computer. It is useful for diagnosing FPGA board connectivity issues.

\b
Examples:
  apio drivers serial list     # List the serial devices.

[Hint] This command executes the utility `lsserial` which can also be invoked
using the command `apio raw -- lsserial <flags>`
"""


@click.command(
    name="list",
    short_help="List the connected serial devices.",
    help=LIST_HELP,
)
def _list_cli():
    """Implements the 'apio drivers serial list' command."""

    # Create the apio context.
    apio_ctx = ApioContext(load_project=False)

    # -- Create the system object
    system = System(apio_ctx)

    # # -- List all connected serial devices
    exit_code = system.lsserial()
    sys.exit(exit_code)


# --- apio drivers serial

SERIAL_HELP = """
The 'apio drivers serial' commands group contains subcommands that are used
to manage the serial drivers on your system.

The subcommands are listed below.
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
    name="serial",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Manage the serial drivers.",
    help=SERIAL_HELP,
)
def cli():
    """Implements the 'apio drivers serial' command."""

    # pass
