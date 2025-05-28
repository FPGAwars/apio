# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio drivers' command group."""

import click
from apio.utils.cmd_util import ApioGroup, ApioSubgroup
from apio.commands import (
    apio_drivers_install,
    apio_drivers_uninstall,
)


# --- apio drivers

# -- Text in the rich-text format of the python rich library.
APIO_DRIVERS_HELP = """
The command group 'apio drivers' contains subcommands to manage the \
drivers on your system.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            apio_drivers_install.cli,
            apio_drivers_uninstall.cli,
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
    """Implements the apio drivers command."""

    # pass
