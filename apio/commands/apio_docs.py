# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio docs' command group."""

import click
from apio.utils.cmd_util import ApioGroup, ApioSubgroup
from apio.apio_context import ApioContext, ApioContextScope
from apio.commands import apio_docs_apio_ini
from apio.common.apio_console import cout


# -- apio docs resources

APIO_DOCS_RESOURCES_HELP = """
The command 'apio docs resources' provides information about apio
related online resources.

\b
Examples:
  apio docs resources     # Provides resources information
"""


@click.command(
    name="resources",
    short_help="Information about online resources.",
    help=APIO_DOCS_RESOURCES_HELP,
)
def _resources_cli():
    """Implements the 'apio docs resources' command."""

    # -- Create the apio context. We don't really need it here but it also
    # -- reads the user preferences and configure the console's colors.
    ApioContext(scope=ApioContextScope.NO_PROJECT)

    cout("TBD", style="cyan")


# --- apio docs

APIO_DOCS_HELP = """
The command group ‘apio docs contains subcommands that provides various
apio documentation and references to online resources.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [apio_docs_apio_ini.cli, _resources_cli],
    )
]


@click.command(
    name="docs",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Read apio documentations.",
    help=APIO_DOCS_HELP,
)
def cli():
    """Implements the apio docs command."""

    # pass
