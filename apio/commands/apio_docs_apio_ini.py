# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio docs apio-ini'."""

import sys
import click
from apio.managers import project
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils import cmd_util
from apio.common.apio_console import (
    docs_text,
    docs_rule,
    cout,
    cerror,
    cstyle,
    DOCS_TITLE,
)


# -- apio docs apio-ini

# -- Text in the markdown format of the python rich library.
APIO_DOCS_APIO_INI_HELP = """
The command 'apio docs apio-ini' provides information about the required \
project file 'apio.ini'.

Examples:[code]
  apio docs apio.ini              # List an overview and all options.
  apio docs apio.ini top-module   # List a single option.[/code]
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
    name="apio.ini",
    cls=cmd_util.ApioCommand,
    short_help="Project file apio.ini documentation.",
    help=APIO_DOCS_APIO_INI_HELP,
)
@click.argument("option", nargs=1, required=False)
def cli(
    # Argument
    option: str,
):
    """Implements the 'apio docs apio-ini' command."""

    # -- Create the apio context. We don't really need it here but it also
    # -- reads the user preferences and configure the console's colors.
    ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- If option was specified, validate it.
    if option:
        if option not in project.OPTIONS:
            cerror(f"No such api.ini option: '{option}'")
            cout(
                "For the list of all apio.ini options, type "
                "'apio docs apio.ini'.",
                style="yellow",
            )
            sys.exit(1)

    # -- If printing all the options, print first the overview.
    if not option:
        docs_text(APIO_INI_DOC)

    # -- Determine options to print
    options = [option] if option else project.OPTIONS.keys()

    # -- Print the initial seperator line.
    docs_rule()
    for opt in options:
        # -- Print option's title.
        is_required = opt in project.REQUIRED_OPTIONS
        req = "REQUIRED" if is_required else "OPTIONAL"
        styled_option = cstyle(opt.upper(), style=DOCS_TITLE)
        cout()
        cout(f"{styled_option} ({req})")

        # -- Print the option's text.
        text = project.OPTIONS[opt]
        docs_text(text)
        docs_rule()
