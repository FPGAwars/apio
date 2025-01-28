# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio preferences' command"""

import click
from rich.table import Table
from rich import box
from apio.common.apio_console import cout, cprint
from apio.utils import cmd_util
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand

# ---- apio preferences list

# -- Text in the markdown format of the python rich library.
APIO_PREFERENCES_LIST_HELP = """
The command 'apio preferences list' lists the current user preferences.

Examples:[code]
  apio preferences list  # List the user preferences.[/code]
"""


# R0801: Similar lines in 2 files
# pylint: disable=R0801
@click.command(
    name="list",
    cls=ApioCommand,
    short_help="List the apio user preferences.",
    help=APIO_PREFERENCES_LIST_HELP,
)
def _list_cli():
    """Implements the 'apio preferences list' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    table = Table(
        show_header=True,
        show_lines=True,
        box=box.SQUARE,
        border_style="dim",
        title="Apio User Preferences",
        padding=(0, 2),
        header_style="cyan",
    )

    # -- Add columnes.
    table.add_column("ITEM", no_wrap=True)
    table.add_column("VALUE", no_wrap=True, min_width=30)

    # -- Add rows.
    value = apio_ctx.profile.preferences.get("colors", "on")
    table.add_row("Colors", value)

    # -- Print title.
    cout("Apio user preferences", style="magenta")

    # -- Render table.
    cout()
    cprint(table)


# ---- apio preferences set

# -- Text in the markdown format of the python rich library.
APIO_PREF_SET_HELP = """
The command 'apio preferences set' allows to set the supported user \
preferences.

Examples:[code]
  apio preferences set --colors on    # Enable colors.
  apio preferences set --colors off   # Disable colors.[/code]

The apio colors are optimized for a terminal windows with a white background.
"""

colors_options = click.option(
    "colors",  # Var name
    "-c",
    "--colors",
    required=True,
    type=click.Choice(["on", "off"], case_sensitive=True),
    help="Set/reset colors mode.",
    cls=cmd_util.ApioOption,
)


@click.command(
    name="set",
    cls=ApioCommand,
    short_help="Set the apio user preferences.",
    help=APIO_PREF_SET_HELP,
)
@colors_options
def _set_cli(colors: str):
    """Implements the 'apio preferences set' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Set the colors preference value.
    apio_ctx.profile.set_preferences_colors(colors)

    # -- Show the result. The new colors preference is already in effect.
    color = apio_ctx.profile.preferences["colors"]
    cout(f"Colors set to [{color}]", style="green")


# --- apio preferences

# -- Text in the markdown format of the python rich library.
APIO_PREFERENCES_HELP = """
The command group 'apio preferences' contains subcommands to manage \
the apio user preferences. These are user configurations that affect all the \
apio projects that use the same apio home directory (e.g. '~/.apio').

The user preference is not part of any apio project and typically are not \
shared when multiple user colaborate on the same project.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _list_cli,
            _set_cli,
        ],
    )
]


@click.command(
    name="preferences",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Manage the apio user preferences.",
    help=APIO_PREFERENCES_HELP,
)
def cli():
    """Implements the apio preferences command."""

    # pass
