# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio docs' command group."""

import sys
import click
from rich.table import Table
from rich import box
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand
from apio.utils import cmd_util
from apio.apio_context import ApioContext, ApioContextScope
from apio.common.styles import BORDER, EMPH1
from apio.managers import project
from apio.common.styles import TITLE, INFO
from apio.common.apio_console import (
    PADDING,
    docs_text,
    docs_rule,
    cout,
    cerror,
    cstyle,
    cprint,
)

# -- apio docs cli

# -- Text in the markdown format of the python rich library.
APIO_DOCS_CLI_HELP = """
The command 'apio docs cli' provides information the Apio's command line \
conventions and features.  \

Examples:[code]
  apio docs cli        # Shoe the cli documentation text.
"""

# -- Text in the markdown format of the python rich library.
APIO_DOCS_CLI_TEXT = """
[apio.title]APIO's COMMAND LINE INTERFACE[/]
This page describes the conventions and features of the apio command line \
interface.

[apio.title]1. APIO'S COMMANDS TREE[/]
Apio commands are organized as a tree of command that start with the root \
command 'apio'. Some command such as 'apio build' has only two level of \
commands while other such as 'apio preferences set' have three and maybe \
more levels. To explore the available commands at each level, type it with \
'-h' to invoke its help message. For example:

[code]  apio -h
  apio docs -h
  apio docs cli -h[/code]

[apio.title]2. APIO'S COMMANDS OPTIONS[/]
Most Apio's commands have options that allow to control their operation. For \
example, the command 'apio build' that has options to control the verbosity \
of its output: \

[code]  apio build --verbose
  apio build --verbose-synth[/code]

For the list of options of each command type it with a '-h' option:

[code]  apio build -h[/code]

[apio.title]3. APIO'S COMMANDS SHORTCUTS[/]
When typing apio commands, it's sufficient to type enough of the command to \
make the selection non ambiguous. For example, the commands below are \
equivalent.

[code]  apio preferences
  apio pref
  apio pr[/code]

However, the command 'apio p' is ambiguous because it matched both  \
'apio preferences' and 'apio packages'.

[apio.title]4. APIO'S SHELL AUTO COMPLETION[/]
Apio's command line processor is based on the Python Click package which \
supports auto completion with some shells. While the were able to make \
it work as a proof of concept, this feature is experimental and is not \
guaranteed to work. More information is available in the Click's \
documentation at https://click.palletsprojects.com/en/stable/shell-completion.
"""


@click.command(
    name="cli",
    cls=cmd_util.ApioCommand,
    short_help="Apio's command line conventions.'",
    help=APIO_DOCS_CLI_HELP,
)
def _cli_cli():
    """Implements the 'apio docs cli' command."""
    docs_text(APIO_DOCS_CLI_TEXT)


# -- apio docs options

# -- Text in the markdown format of the python rich library.
APIO_DOCS_OPTIONS_HELP = """
The command 'apio docs options' provides information about the required \
project file 'apio.ini'.

Examples:[code]
  apio docs options              # List an overview and all options.
  apio docs options top-module   # List a single option.[/code]
"""

# -- Text in the markdown format of the python rich library.
APIO_INI_DOC = """
Every Apio project is required to have an 'apio.ini' project configuration \
file. These are properties text files with '#' comments and a single section \
called '\\[env]' that contains the required and optional options for this \
project.

Example:[code]
  \\[env]
  board = alhambra-ii   # Board id
  top-module = my_main  # Top module name[/code]

Following is a list of the apio.ini options and their descriptions.
"""


@click.command(
    name="options",
    cls=cmd_util.ApioCommand,
    short_help="Apio.ini options documentation.",
    help=APIO_DOCS_OPTIONS_HELP,
)
@click.argument("option", nargs=1, required=False)
def _options_cli(
    # Argument
    option: str,
):
    """Implements the 'apio docs options' command."""

    # -- Create the apio context. We don't really need it here but it also
    # -- reads the user preferences and configure the console's colors.
    ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- If option was specified, validate it.
    if option:
        if option not in project.OPTIONS:
            cerror(f"No such api.ini option: '{option}'")
            cout(
                "For the list of all apio.ini options, type "
                "'apio docs options'.",
                style=INFO,
            )
            sys.exit(1)

    # -- If printing all the options, print first the overview.
    if not option:
        docs_text(APIO_INI_DOC)

    # -- Determine options to print
    options = [option] if option else project.OPTIONS.keys()

    # -- Print the initial separator line.
    docs_rule()
    for opt in options:
        # -- Print option's title.
        is_required = opt in project.REQUIRED_OPTIONS
        req = "REQUIRED" if is_required else "OPTIONAL"
        styled_option = cstyle(opt.upper(), style=TITLE)
        cout()
        cout(f"{styled_option} ({req})")

        # -- Print the option's text.
        text = project.OPTIONS[opt]
        docs_text(text)
        docs_rule()


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
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio Related Resources",
        title_justify="left",
    )

    table.add_column("RESOURCE", no_wrap=True)
    table.add_column("RESOURCE LOCATION", no_wrap=True, style=EMPH1)

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
apio documentation and references information.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [_cli_cli, _options_cli, _resources_cli],
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
