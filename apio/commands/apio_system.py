# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio system' command"""

import importlib.metadata
import click
from apio import util
from apio.apio_context import ApioContext, ApioContextScope
from apio.cmd_util import ApioGroup, ApioSubgroup


# ------ apio system info

INFO_HELP = """
The command ‘apio system info’ provides general information about your system
and Apio installation, which is useful for diagnosing Apio installation issues.

\b
Examples:
  apio system info       # Show platform id and info.

[Advanced] The default location of the Apio home directory, where preferences
and packages are stored, is in the .apio directory under the user’s home
directory. This location can be changed using the APIO_HOME_DIR environment
variable.

"""


@click.command(
    name="info",
    short_help="Show platform id and other info.",
    help=INFO_HELP,
)
def _info_cli():
    """Implements the 'apio system info' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Print apio version.
    click.secho("Apio version    ", nl=False)
    click.secho(importlib.metadata.version("apio"), fg="cyan")

    # -- Print python version.
    click.secho("Python version  ", nl=False)
    click.secho(util.get_python_version(), fg="cyan")

    # -- Print platform id.
    click.secho("Platform id     ", nl=False)
    click.secho(apio_ctx.platform_id, fg="cyan")

    # -- Print apio package directory.
    click.secho("Python package  ", nl=False)
    click.secho(util.get_path_in_apio_package(""), fg="cyan")

    # -- Print apio home directory.
    click.secho("Apio home       ", nl=False)
    click.secho(apio_ctx.home_dir, fg="cyan")

    # -- Print apio home directory.
    click.secho("Apio packages   ", nl=False)
    click.secho(apio_ctx.packages_dir, fg="cyan")


# ------ apio system platforms

PLATFORMS_HELP = """
The command ‘apio system platforms’ lists the platform IDs supported by Apio,
with the effective platform ID of your system highlighted.

\b
Examples:
  apio system platforms   # List supported platform ids.

[Advanced] The automatic platform ID detection of Apio can be overridden by
defining a different platform ID using the APIO_PLATFORM environment variable.
"""


@click.command(
    name="platforms",
    short_help="List supported platforms ids.",
    help=PLATFORMS_HELP,
)
def _platforms_cli():
    """Implements the 'apio system platforms' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Print title line
    click.secho(
        f"  {'[PLATFORM ID]':18} " f"{'[DESCRIPTION]'}",
        fg="magenta",
    )

    # -- Print a line for each platform id.
    for platform_id, platform_info in apio_ctx.platforms.items():
        # -- Get next platform's info.
        description = platform_info.get("description")
        # -- Determine if it's the current platform id.
        fg = "green" if platform_id == apio_ctx.platform_id else None
        # -- Print the line.
        click.secho(f"  {platform_id:18} {description}", fg=fg)


# ------ apio system

SYSTEM_HELP = """
The command group ‘apio system’ contains subcommands that provide information
about the system and Apio’s installation.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _platforms_cli,
            _info_cli,
        ],
    )
]


@click.command(
    name="system",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Provides system info.",
    help=SYSTEM_HELP,
)
def cli():
    """Implements the 'apio system' command group."""

    # pass
