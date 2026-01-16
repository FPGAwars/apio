# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio info' command"""

import sys
from typing import List
from datetime import date
import click
from rich.table import Table
from rich.text import Text
from rich import box
from rich.color import ANSI_COLOR_NAMES
from apio.common.apio_styles import BORDER, EMPH1, EMPH2, EMPH3, INFO
from apio.utils import util
from apio.commands import options
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand
from apio.common.apio_themes import THEMES_TABLE, THEME_LIGHT
from apio.profile import get_datetime_stamp, days_between_datetime_stamps
from apio.common.apio_console import (
    PADDING,
    cout,
    cwrite,
    cstyle,
    ctable,
    get_theme,
    configure,
)


# ------ apio info system


def construct_remote_config_status_str(apio_ctx: ApioContext) -> str:
    """Query the apio profile and construct a short string indicating the
    status of the cached remote config."""
    config = apio_ctx.profile.remote_config
    metadata = config.get("metadata", {})
    timestamp_now = get_datetime_stamp()
    config_status = []
    # -- Handle the case of a having a cached config.
    if config:
        config_days = days_between_datetime_stamps(
            metadata.get("loaded-at", ""), timestamp_now, None
        )
        # -- Determine cache age in days, if possible.
        if config_days is not None:
            config_status.append(
                f"Cached {util.plurality(config_days, 'day')} ago"
            )
        else:
            config_status.append("Cached")
        # -- Indicate if there is a sign of a failed refresh attempt.
        if "refresh-failure-on" in metadata:
            config_status.append("refresh failed.")
    # -- Handle the case of not having a cached config.
    else:
        config_status.append("Not cached")

    # -- Concatenate and return.
    config_status = ", ".join(config_status)
    return config_status


# -- Text in the rich-text format of the python rich library.
APIO_INFO_SYSTEM_HELP = """
The command 'apio info system' provides general information about your \
system and Apio CLI installation, which is useful for diagnosing Apio \
CLI installation issues.

Examples:[code]
  apio info system   # System info.[/code]

[NOTE] For programmatic access to this information use 'apio api get-system'.

[ADVANCED] The default location of the Apio CLI home directory, \
where apio saves preferences and packages, is in the '.apio' directory \
under the user home directory but can be changed using the system \
environment variable 'APIO_HOME'.
"""


@click.command(
    name="system",
    cls=ApioCommand,
    short_help="Show system information.",
    help=APIO_INFO_SYSTEM_HELP,
)
def _system_cli():
    """Implements the 'apio info system' command."""

    # -- Create the apio context. We use 'cached_ok' to cause the config
    # -- to be loaded so we can report it.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
    )

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=True,
        padding=PADDING,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio System Information",
        title_justify="left",
    )

    table.add_column("ITEM", no_wrap=True, min_width=20)
    table.add_column("VALUE", no_wrap=True, style=EMPH1)

    # -- Add rows
    table.add_row("Apio CLI version", util.get_apio_version_str())
    table.add_row("Release info", util.get_apio_release_info() or "(none)")
    table.add_row("Python version", util.get_python_version())
    table.add_row("Python executable", sys.executable)
    table.add_row("Platform id", apio_ctx.platform_id)
    table.add_row("Scons shell id", apio_ctx.scons_shell_id)
    table.add_row("VSCode debugger", str(util.is_under_vscode_debugger()))
    table.add_row("Pyinstaller", str(util.is_pyinstaller_app()))
    table.add_row(
        "Apio Python package", str(util.get_path_in_apio_package(""))
    )
    table.add_row("Apio home dir", str(apio_ctx.apio_home_dir))
    table.add_row("Apio packages dir", str(apio_ctx.apio_packages_dir))
    table.add_row("Remote config URL", apio_ctx.profile.remote_config_url)
    table.add_row(
        "Remote config status", construct_remote_config_status_str(apio_ctx)
    )
    table.add_row(
        "Veriable formatter",
        str(apio_ctx.apio_packages_dir / "verible/bin/verible-verilog-format"),
    )
    table.add_row(
        "Veriable language server",
        str(apio_ctx.apio_packages_dir / "verible/bin/verible-verilog-ls"),
    )

    # -- Render the table.
    cout()
    ctable(table)
    cout(
        "To force a remote config refresh, run 'apio packages install'.",
        style=INFO,
    )


# ------ apio info platforms

# -- Text in the rich-text format of the python rich library.
APIO_INFO_PLATFORMS_HELP = """
The command 'apio info platforms' lists the platform IDs supported by Apio, \
with the effective platform ID of your system highlighted.

Examples:[code]
  apio info platforms   # List supported platform ids.[/code]

The automatic platform ID detection of Apio can be overridden by \
defining a different platform ID using the APIO_PLATFORM environment variable.
"""


@click.command(
    name="platforms",
    cls=ApioCommand,
    short_help="Supported platforms.",
    help=APIO_INFO_PLATFORMS_HELP,
)
def _platforms_cli():
    """Implements the 'apio info platforms' command."""

    # Create the apio context.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
    )

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=True,
        padding=PADDING,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio Supported Platforms",
        title_justify="left",
    )

    table.add_column("  PLATFORM ID", no_wrap=True)
    table.add_column("TYPE", no_wrap=True)
    table.add_column("VARIANT", no_wrap=True)

    # -- Add rows.
    for platform_id, platform_info in apio_ctx.platforms.items():
        platform_type = platform_info.get("type")
        platform_variant = platform_info.get("variant")

        # -- Mark the current platform.
        if platform_id == apio_ctx.platform_id:
            style = EMPH3
            marker = "* "
        else:
            style = None
            marker = "  "

        table.add_row(
            f"{marker}{platform_id}",
            platform_type,
            platform_variant,
            style=style,
        )

    # -- Render the table.
    cout()
    ctable(table)


# ------ apio info colors

# -- Text in the rich-text format of the python rich library.
APIO_INFO_COLORS_HELP = """
The command 'apio info colors' shows how ansi colors are rendered on \
the platform, and is typically used to diagnose color related issues.

The command shows the themes colors even if the current theme is 'no-colors'.

Examples:[code]
  apio info colors          # Rich library output (default)
  apio inf col -p           # Using shortcuts.[/code]
"""


@click.command(
    name="colors",
    cls=ApioCommand,
    short_help="Colors table.",
    help=APIO_INFO_COLORS_HELP,
)
def _colors_cli():
    """Implements the 'apio info colors' command."""

    # -- This initializes the output console.
    ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
    )

    # -- Print title.
    cout("", "ANSI Colors", "")

    # -- Create a reversed num->name map
    lookup = {}
    for name, num in ANSI_COLOR_NAMES.items():
        assert 0 <= num <= 255
        lookup[num] = name

    # -- Make sure the current theme supports colors, otherwise they will
    # -- suppressed
    if get_theme().colors_enabled:
        saved_theme_name = None
    else:
        saved_theme_name = get_theme().name
        configure(theme_name=THEME_LIGHT.name)

    # -- Print the table.
    num_rows = 64
    num_cols = 4
    for row in range(num_rows):
        values = []
        for col in range(num_cols):
            num = row + (col * num_rows)
            name = lookup.get(num, None)
            if name is None:
                # -- No color name.
                values.append(" " * 24)
            else:
                # -- Color name is available.
                # -- Note that the color names and styling is always done by
                # -- the rich library regardless of the choice of output.
                s = f"{num:3} {name:20}"
                values.append(cstyle(s, style=name))

        # -- Construct the line.
        line = "   ".join(values)

        # -- Output the line.
        cout(line)

    cout()

    # -- Restore the original theme.
    if saved_theme_name:
        configure(theme_name=saved_theme_name)


# ------ apio info themes

# -- Text in the rich-text format of the python rich library.
APIO_INFO_THEMES_HELP = """
The command 'apio info themes' shows the colors of the Apio themes. It can \
be used to select the theme that works the best for you. Type  \
'apio preferences -h' for information on our to select a theme.

The command shows colors even if the current theme is 'no-colors'.

[code]
Examples:
  apio info themes          # Show themes colors
  apio inf col -p           # Using shortcuts.[/code]
"""


@click.command(
    name="themes",
    cls=ApioCommand,
    short_help="Show apio themes.",
    help=APIO_INFO_THEMES_HELP,
)
def _themes_cli():
    """Implements the 'apio info themes' command."""

    # -- This initializes the output console.
    ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
    )

    # -- Collect the list of apio list names.
    style_names = set()
    for theme_info in THEMES_TABLE.values():
        style_names.update(list(theme_info.styles.keys()))
    style_names = sorted(list(style_names), key=str.lower)

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=True,
        padding=PADDING,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio Themes Style Colors",
        title_justify="left",
    )

    # -- Get selected theme
    selected_theme = get_theme()
    selected_theme_name = selected_theme.name

    # -- Add the table columns, one per theme.
    for theme_name, theme in THEMES_TABLE.items():
        assert theme_name == theme.name
        column_name = theme_name.upper()
        if theme_name == selected_theme_name:
            column_name = f"*{column_name}*"
        table.add_column(column_name, no_wrap=True, justify="center")

    # -- Append the table rows
    for style_name in style_names:
        row_values: List[Text] = []
        for theme_name, theme_info in THEMES_TABLE.items():
            # Get style
            colors_enabled = theme_info.colors_enabled
            if colors_enabled:
                if style_name not in theme_info.styles:
                    styled_text = Text("---")
                else:
                    styled_text = Text(
                        style_name, style=theme_info.styles[style_name]
                    )
            else:
                styled_text = Text(style_name)

            # -- Apply the style
            row_values.append(styled_text)

        table.add_row(*row_values)

    # -- Make sure the current theme supports colors, otherwise they will
    # -- suppressed
    if get_theme().colors_enabled:
        saved_theme_name = None
    else:
        saved_theme_name = get_theme().name
        configure(theme_name=THEME_LIGHT.name)

    # -- Render the table.
    cout()
    ctable(table)

    if saved_theme_name:
        configure(theme_name=saved_theme_name)

    cout("To change your theme use 'apio preferences -t ...'", style=INFO)
    cout()


# ------ apio info commands


def _list_boards_table_format(commands):
    """Format and output the commands table. 'commands' is a sorted
    list of [command_name, command_description]
    """
    # -- Generate the table.
    table = Table(
        show_header=True,
        show_lines=True,
        padding=PADDING,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio commands",
        title_justify="left",
    )

    table.add_column("APIO COMMAND", no_wrap=True, min_width=20, style=EMPH2)
    table.add_column("DESCRIPTION", no_wrap=True)

    for cmd in commands:
        table.add_row(cmd[0], cmd[1])

    # -- Render the table.
    cout()
    ctable(table)


def _list_boards_docs_format(commands):
    """Format and output the commands markdown doc. 'commands' is a sorted
    list of [command_name, command_description]
    """

    header1 = "COMMAND"
    header2 = "DESCRIPTION"

    # -- Replace the command names with markdown link to the command doc page.
    tagged_commands = [
        [f"[{c[0]}](cmd-apio-{c[0]}.md)", c[1]] for c in commands
    ]

    # -- Determine column sizes
    w1 = max(len(header1), *(len(cmd[0]) for cmd in tagged_commands))
    w2 = max(len(header2), *(len(cmd[1]) for cmd in tagged_commands))

    # -- Print page header
    today = date.today()
    today_str = f"{today.strftime('%B')} {today.day}, {today.year}"
    cwrite("\n<!-- BEGIN generation by 'apio commands --docs' -->\n")
    cwrite("\n# Apio CLI commands\n")
    cwrite(
        f"\nThis markdown page was generated automatically on {today_str}.\n\n"
    )

    # -- Table header
    cwrite(
        "| {0} | {1} |\n".format(
            header1.ljust(w1),
            header2.ljust(w2),
        )
    )

    cwrite(
        "| {0} | {1} |\n".format(
            "-" * w1,
            "-" * w2,
        )
    )

    # -- Add the rows
    for tagged_cmd in tagged_commands:
        cwrite(
            "| {0} | {1} |\n".format(
                tagged_cmd[0].ljust(w1),
                tagged_cmd[1].ljust(w2),
            )
        )

    # -- All done.
    cwrite("\n<!-- END generation by 'apio commands --docs' -->\n\n")


# -- Text in the rich-text format of the python rich library.
APIO_INFO_COMMANDS_HELP = """
The command 'apio info commands' lists the the available apio commands \
in a table format. If the option '--docs' is specified, the command outputs \
the list as a markdown document that is used to automatically update the \
Apio documentation.

Examples:[code]
  apio info commands
  apio info commands --docs > docs/commands-list.md[/code]
"""


@click.command(
    name="commands",
    cls=ApioCommand,
    short_help="Show apio commands.",
    help=APIO_INFO_COMMANDS_HELP,
)
@options.docs_format_option
def _commands_cli(
    # Options
    docs,
):
    """Implements the 'apio info commands' command."""

    # -- We perform this lazy cyclic import here to allow the two modules
    # -- to initialize properly without a cyclic import.
    #
    # pylint: disable=import-outside-toplevel
    # pylint: disable=cyclic-import
    from apio.commands import apio as apio_main

    # -- This initializes the output console.
    ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.IGNORE_PACKAGES,
    )

    # -- Collect commands as a list of <name, description>
    commands = []
    for subgroup in apio_main.SUBGROUPS:
        for cmd in subgroup.commands:
            commands.append([cmd.name, cmd.get_short_help_str()])

    # -- Sort the commands list alphabetically.
    commands.sort()

    # -- Generate the output
    if docs:
        _list_boards_docs_format(commands)
    else:
        _list_boards_table_format(commands)


# ------ apio info

# -- Text in the rich-text format of the python rich library.
APIO_INFO_HELP = """
The command group 'apio info' contains subcommands that provide \
additional information about Apio and your system.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _system_cli,
            _platforms_cli,
            _colors_cli,
            _themes_cli,
            _commands_cli,
        ],
    ),
]


@click.command(
    name="info",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Apio's info and info.",
    help=APIO_INFO_HELP,
)
def cli():
    """Implements the 'apio info' command group."""

    # pass
