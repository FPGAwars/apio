# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio docs apio-ini'."""

import click
from rich.theme import Theme
from rich.console import Console
from apio.managers import project


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

    console = Console(
        width=70,
        theme=Theme(
            {
                "repr.str": "cyan bold",
                "code": "cyan bold",
            }
        ),
    )

    # -- Print the overview test.
    console.print(APIO_INI_DOC)

    # -- Print the initial seperator line.
    console.rule(style="blue")
    for option, text in project.OPTIONS.items():
        # -- Print the next option.
        is_required = option in project.REQUIRED_OPTIONS
        req = "REQUIRED" if is_required else "OPTIONAL"
        console.print(f"\n[magenta bold]{option.upper()}[/] ({req})")
        # -- Print a seperator line.
        console.print(text)
        console.rule(style="blue")
