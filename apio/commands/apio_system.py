# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio system' command"""

import click
from click import secho
from apio import util
from apio.apio_context import ApioContext, ApioContextScope
from apio.cmd_util import ApioGroup, ApioSubgroup


# ------ apio system info

APIO_SYSTEM_INFO_HELP = """
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
    help=APIO_SYSTEM_INFO_HELP,
)
def _info_cli():
    """Implements the 'apio system info' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Print apio version.
    secho("Apio version:     ", nl=False)
    secho(util.get_apio_version(), fg="cyan", bold=True)

    # -- Print python version.
    secho("Python version:   ", nl=False)
    secho(util.get_python_version(), fg="cyan", bold=True)

    # -- Print platform id.
    secho("Platform id:      ", nl=False)
    secho(apio_ctx.platform_id, fg="cyan", bold=True)

    # -- Print apio package directory.
    secho("Python package:   ", nl=False)
    secho(util.get_path_in_apio_package(""), fg="cyan", bold=True)

    # -- Print apio home directory.
    secho("Apio home:        ", nl=False)
    secho(apio_ctx.home_dir, fg="cyan", bold=True)

    # -- Print apio home directory.
    secho("Apio packages:    ", nl=False)
    secho(apio_ctx.packages_dir, fg="cyan", bold=True)


# ------ apio system platforms

APIO_SYSTEM_PLATFORMS_HELP = """
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
    help=APIO_SYSTEM_PLATFORMS_HELP,
)
def _platforms_cli():
    """Implements the 'apio system platforms' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Print title line
    secho(
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
        secho(f"  {platform_id:18} {description}", fg=fg)


# ------ apio system

APIO_SYSTEM_HELP = """
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
    help=APIO_SYSTEM_HELP,
)
def cli():
    """Implements the 'apio system' command group."""

    # pass
