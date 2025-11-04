# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio preferences' command"""

import sys
from io import StringIO
import click
from rich.console import Console
from rich.table import Table
from rich import box
from apio.commands import options
from apio.common import apio_themes
from apio.common.apio_console import cout, ctable
from apio.common.apio_styles import BORDER, EMPH1, SUCCESS
from apio.common.apio_themes import THEMES_TABLE, THEMES_NAMES, DEFAULT_THEME
from apio.utils import cmd_util
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.utils.cmd_util import ApioCommand

# --- apio preferences


def _list_themes_colors():
    width = 16

    # -- For color styling we use an independent rich Console to bypass
    # -- the current theme of apio_console.
    cons = Console(color_system="auto", force_terminal=True)

    # -- Print title lines.
    print()
    values = []
    for theme_name in THEMES_NAMES:
        s = f"[{theme_name.upper()}]"
        values.append(f"{s:{width}}")
    print("  ".join(values))

    # -- Print a line for each style name.
    for style_name in DEFAULT_THEME.styles.keys():
        values = []
        for theme_name in THEMES_NAMES:
            theme = THEMES_TABLE[theme_name]
            # -- For themes with disabled colors we disable the color styling.
            style = theme.styles[style_name] if theme.colors_enabled else None
            # -- Format for a fixed with.
            s = f"{style_name:{width}}"
            # -- Install a capture buffer.
            cons.file = StringIO()
            # -- Output to buffer, with optional style.
            cons.out(s, style=style, end="")
            # -- Get the captured output.
            values.append(cons.file.getvalue())
        # -- Print the line with style colors.
        print("  ".join(values))

    print()


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
    ctable(table)


def _set_theme(apio_ctx: ApioContext, theme_name: str):
    """Sets the colors theme to the given theme name."""

    # -- Set the colors preference value.
    apio_ctx.profile.set_preferences_theme(theme_name)

    # -- Show the result. The new colors preference is already in effect.
    confirmed_theme = apio_ctx.profile.preferences["theme"]
    cout(f"Theme set to [{confirmed_theme}]", style=SUCCESS)


# -- Text in the rich-text format of the python rich library.
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

colors_option = click.option(
    "colors",  # Var name
    "-c",
    "--colors",
    is_flag=True,
    help="List themes colors.",
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
@colors_option
@options.list_option_gen(short_help="List the preferences.")
def cli(
    cmd_ctx: click.Context,
    # -- Options
    theme_name: str,
    colors: bool,
    list_: bool,
):
    """Implements the apio preferences command."""

    # -- At most one of those.
    cmd_util.check_at_most_one_param(
        cmd_ctx, ["theme_name", "colors", "list_"]
    )

    # -- Handle theme setting.
    if theme_name:
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )
        _set_theme(apio_ctx, theme_name)
        sys.exit(0)

    # -- Handle preferences settings.
    if list_:
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )
        _list_preferences(apio_ctx)
        sys.exit(0)

    if colors:
        _list_themes_colors()
        sys.exit(0)

    # -- If nothing to do then print help and exit
    click.echo(cmd_ctx.get_help())
    sys.exit(0)
