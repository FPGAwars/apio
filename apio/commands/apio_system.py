# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio system' command"""

import click
from rich.table import Table
from rich import box
from rich.color import ANSI_COLOR_NAMES
from apio.common.apio_console import cprint, PADDING, cout, cstyle
from apio.common.styles import BORDER, EMPH1, EMPH3
from apio.utils import util, cmd_util
from apio.utils.util import nameof
from apio.utils.cmd_util import check_at_most_one_param
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand


# ------ apio system info

# -- Text in the markdown format of the python rich library.
APIO_SYSTEM_INFO_HELP = """
The command 'apio system info' provides general information about your \
system and Apio installation, which is useful for diagnosing Apio \
installation issues.

Examples:[code]
  apio system info   # Show general info.[/code]

[b][Advanced][/b] The default location of the Apio home directory, \
where apio saves preferences and packages, is in the '.apio' directory \
under the user home directory but can be changed using the system \
environment variable 'APIO_HOME_DIR'.
"""


# R0801: Similar lines in 2 files
# pylint: disable=R0801
@click.command(
    name="info",
    cls=ApioCommand,
    short_help="Show platform id and other info.",
    help=APIO_SYSTEM_INFO_HELP,
)
def _info_cli():
    """Implements the 'apio system info' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

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

    table.add_column("ITEM", no_wrap=True)
    table.add_column("VALUE", no_wrap=True, style=EMPH1)

    # -- Add rows
    table.add_row("Apio version", util.get_apio_version())
    table.add_row("Python version ", util.get_python_version())
    table.add_row("Platform id ", apio_ctx.platform_id)
    table.add_row("Python package ", str(util.get_path_in_apio_package("")))
    table.add_row("Apio home ", str(apio_ctx.home_dir))
    table.add_row("Apio packages ", str(apio_ctx.packages_dir))
    table.add_row(
        "Veriable language server ",
        str(apio_ctx.packages_dir / "verible/bin/verible-verilog-ls"),
    )

    # -- Render the table.
    cout()
    cprint(table)


# ------ apio system platforms

APIO_SYSTEM_PLATFORMS_HELP = """
The command 'apio system platforms' lists the platform IDs supported by Apio, \
with the effective platform ID of your system highlighted.

[code]Examples:
  apio system platforms   # List supported platform ids.[/code]

[Advanced] The automatic platform ID detection of Apio can be overridden by \
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

    table.add_column("PLATFORM ID", min_width=20, no_wrap=True)
    table.add_column("DESCRIPTION", min_width=30, no_wrap=True)

    # -- Add rows.
    for platform_id, platform_info in apio_ctx.platforms.items():
        description = platform_info.get("description")

        # -- Mark the current platform.
        if platform_id == apio_ctx.platform_id:
            style = EMPH3
            marker = "* "
        else:
            style = None
            marker = "  "

        table.add_row(f"{marker}{platform_id}", f"{description}", style=style)

    # -- Render the table.
    cout()
    cprint(table)


# ------ apio system colors

# -- Text in the markdown format of the python rich library.
APIO_SYSTEM_COLORS_HELP = """
The command 'apio system colors' shows how ansi colors are rendered on \
the platform, and is typically used to diagnose color related issues. \
While the color name and styling is always handled by the Python Rich \
library, the output is done via three different libraries, based on \
the user's selection.

[code]
Examples:
  apio system colors          # Rich library output (default)
  apio system colors --rich   # Same as above.
  apio system colors --click  # Click library output.
  apio system colors --print  # Python's print() output.
  apio sys col -p             # Using shortcuts.[/code]
"""

rich_option = click.option(
    "rich_",  # Var name.
    "-r",
    "--rich",
    is_flag=True,
    help="Output using the rich lib.",
    cls=cmd_util.ApioOption,
)

click_option = click.option(
    "click_",  # Var name.
    "-c",
    "--click",
    is_flag=True,
    help="Output using the click lib.",
    cls=cmd_util.ApioOption,
)

print_option = click.option(
    "print_",  # Var name.
    "-p",
    "--print",
    is_flag=True,
    help="Output using python's print().",
    cls=cmd_util.ApioOption,
)


# R0801: Similar lines in 2 files
# pylint: disable=R0801
# pylint: disable=too-many-locals
@click.command(
    name="colors",
    cls=ApioCommand,
    short_help="Show colors table.",
    help=APIO_SYSTEM_COLORS_HELP,
)
@click.pass_context
@rich_option
@click_option
@print_option
def _colors_cli(
    cmd_ctx: click.Context,
    # options
    rich_: bool,
    click_: bool,
    print_: bool,
):
    """Implements the 'apio system colors' command."""

    # -- Allow at most one of --click and --print.
    check_at_most_one_param(cmd_ctx, nameof(rich_, click_, print_))

    # -- Select by output type.
    if click_:
        mode = "CLICK"
        output_func = click.echo
    elif print_:
        mode = "PRINT"
        output_func = print
    else:
        mode = "RICH"
        output_func = cout

    # -- Print title.
    cout("", f"ANSI Colors [{mode} mode]", "")

    # -- Create a reversed num->name map
    lookup = {}
    for name, num in ANSI_COLOR_NAMES.items():
        assert 0 <= num <= 255
        lookup[num] = name

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
        output_func(line)

    cout()


# ------ apio system

# -- Text in the markdown format of the python rich library.
APIO_SYSTEM_HELP = """
The command group 'apio system' contains subcommands that provide \
information about the system and Apio’s installation.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _platforms_cli,
            _info_cli,
            _colors_cli,
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
