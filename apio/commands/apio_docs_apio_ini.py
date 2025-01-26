# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio docs apio-ini'."""

import click
from apio.managers import project
from apio.apio_context import ApioContext, ApioContextScope
from apio.common.apio_console import docs_text, docs_rule, cout, cstyle


# -- apio docs apio-ini

APIO_DOCS_APIO_INI_HELP = """
The command 'apio docs apio-ini' provides information about the required
apio.ini project file.

\b
Examples:
  apio docs apio-ini           # Provide information about apio.ini
  apio docs apio-ini  | less   # Same but with paging.
"""

APIO_INI_DOC = """
Every apio project is required to have an 'apio.ini' project configuration \
file. These are properties text files with \
'#' comments, and a single section called '[env]' that contains the required \
an optional options for this project.

Example:[code]
  # -- My FPGA project.
  \\[env]
  board = alhambra-ii
  top-module = my_main[/]

Following is a list of the valid 'apio.ini' options and their descriptions.
"""


@click.command(
    name="apio.ini",
    short_help="Project file apio.ini documentation.",
    help=APIO_DOCS_APIO_INI_HELP,
)
def cli():
    """Implements the 'apio docs apio-ini' command."""

    # -- Create the apio context. We don't really need it here but it also
    # -- reads the user preferences and configure the console's colors.
    ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Print the overview test.
    docs_text(APIO_INI_DOC)

    # -- Print the initial seperator line.
    docs_rule()
    for option, text in project.OPTIONS.items():
        # -- Print option's title.
        is_required = option in project.REQUIRED_OPTIONS
        req = "REQUIRED" if is_required else "OPTIONAL"
        styled_option = cstyle(option.upper(), style="magenta")
        cout()
        cout(f"{styled_option} ({req})")

        # -- Print the option's text.
        docs_text(text)
        docs_rule()
