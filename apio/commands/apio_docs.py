# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio docs' command group."""

import click
from rich.table import Table
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand
from apio.apio_context import ApioContext, ApioContextScope
from apio.commands import apio_docs_options
from apio.common.apio_console import cprint, cout, docs_text, PADDING

# -- apio docs resources

# -- Text in the markdown format of the python rich library.
APIO_DOCS_RESOURCES_HELP = """
The command 'apio docs resources' provides information about apio \
related online resources.

Examples:[code]
  apio docs resources   # Provides resources information[/code]
"""

# -- Text in markdown in rich library format.
APIO_DOCS_RESOURCES_SUMMARY = """
The table below provides a few Apio and FPGA design-related resources.

For additional information about specific boards, FPGAs, or tools such as \
[b]yosys[/] and [b]verible[/], consult their respective documentation.

[b]Shawn Hymel's[/] excellent video series on YouTube is based on an older \
version of Apio with a slightly different command set that achieves the \
same functionality.
"""


# R0801: Similar lines in 2 files
# pylint: disable=R0801
@click.command(
    name="resources",
    cls=ApioCommand,
    short_help="Information about online resources.",
    help=APIO_DOCS_RESOURCES_HELP,
)
def _resources_cli():
    """Implements the 'apio docs resources' command."""

    # -- Create the apio context. We don't really need it here but it also
    # -- reads the user preferences and configure the console's colors.
    ApioContext(scope=ApioContextScope.NO_PROJECT)

    docs_text(APIO_DOCS_RESOURCES_SUMMARY, width=73)

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=True,
        padding=PADDING,
        border_style="dim",
        title="Apio Related Resources",
        title_justify="left",
    )

    table.add_column("RESOURCE", no_wrap=True)
    table.add_column("RESOURCE LOCATION", no_wrap=True, style="cyan")

    # -- Add rows
    table.add_row(
        "Apio documentation", "https://github.com/FPGAwars/apio/wiki"
    )

    table.add_row(
        "Shwan Hymel series", "https://www.youtube.com/watch?v=lLg1AgA2Xoo"
    )
    table.add_row("Apio repository", "https://github.com/FPGAwars/apio")
    table.add_row(
        "Apio requests and bugs", "https://github.com/FPGAwars/apio/issues"
    )
    table.add_row("Apio Pypi package", "https://pypi.org/project/apio")
    table.add_row("IceStudio (Apio with GUI)", "https://icestudio.io")
    table.add_row("FPGAwars (FPGA resources)", "https://fpgawars.github.io")
    table.add_row(
        "Alhambra-ii FPGA board.", "https://alhambrabits.com/alhambra"
    )

    # -- Render the table.
    cout()
    cprint(table)


# --- apio docs

# -- Text in the markdown format of the python rich library.
APIO_DOCS_HELP = """
The command group 'apio docs' contains subcommands that provides various \
apio documentation and references to online resources.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [apio_docs_options.cli, _resources_cli],
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
