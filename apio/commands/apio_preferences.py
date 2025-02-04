# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio preferences' command"""

import sys
import click
from rich.table import Table
from rich import box
from apio.commands import options
from apio.common import apio_themes
from apio.common.apio_console import cout, cprint
from apio.common.apio_styles import BORDER, EMPH1, SUCCESS
from apio.utils import cmd_util
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils.cmd_util import ApioCommand

# --- apio preferences


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def _list_preferences(apio_ctx: ApioContext):
    """Lists the preferences."""

    table = Table(
        show_header=True,
        show_lines=True,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio User Preferences",
        title_justify="left",
        padding=(0, 2),
    )

    # -- Add columns.
    table.add_column("ITEM", no_wrap=True)
    table.add_column("VALUE", no_wrap=True, style=EMPH1, min_width=30)

    # -- Add rows.
    value = apio_ctx.profile.preferences.get("theme", "light")
    table.add_row("Theme name", value)

    # -- Render table.
    cout()
    cprint(table)


def _set_theme(apio_ctx: ApioContext, theme_name: str):
    """Sets the colors theme to the given theme name."""

    # -- Set the colors preference value.
    apio_ctx.profile.set_preferences_theme(theme_name)

    # -- Show the result. The new colors preference is already in effect.
    confirmed_theme = apio_ctx.profile.preferences["theme"]
    cout(f"Theme set to [{confirmed_theme}]", style=SUCCESS)


# -- Text in the markdown format of the python rich library.
APIO_PREFERENCES_HELP = """
The command 'apio preferences' allows to view and manage the setting of the \
apio's user's preferences. These settings are stored in the 'profile.json' \
file in the apio home directory (e.g. '~/.apio') and apply to all \
apio projects.

Examples:[code]
  apio preferences -t light       # Colors for light backgrounds.
  apio preferences -t dark        # Colors for dark backgrounds.
  apio preferences -t no-colors   # No colors.
  apio preferences --list         # List current preferences.
  apio pref -t dark               # Using command shortcut.[/code]
"""


theme_option = click.option(
    "theme_name",  # Var name
    "-t",
    "--theme",
    type=click.Choice(apio_themes.THEMES_NAMES, case_sensitive=True),
    help="Set colors theme name.",
    cls=cmd_util.ApioOption,
)


@click.command(
    name="preferences",
    cls=ApioCommand,
    short_help="Manage the apio user preferences.",
    help=APIO_PREFERENCES_HELP,
)
@click.pass_context
@theme_option
@options.list_option_gen(help="List the preferences.")
def cli(
    cmd_ctx: click.Context,
    # -- Options
    theme_name: str,
    list_: bool,
):
    """Implements the apio preferences command."""

    # -- If nothing to do print help and exit
    if not (theme_name or list_):
        click.echo(cmd_ctx.get_help())
        sys.exit(0)

    # -- Construct an apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Handle theme setting.
    if theme_name:
        _set_theme(apio_ctx, theme_name)

    # -- Handle preferences settings.
    if list_:
        _list_preferences(apio_ctx)
