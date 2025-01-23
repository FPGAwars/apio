# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio docs apio-ini'."""

import click
from rich.console import Console
from apio.managers import project


# -- apio docs apio-ini

APIO_DOCS_RESOURCES_HELP = """
The command 'apio docs apio-ini' provides information about the apio.ini
project file.

\b
Examples:
  apio docs apio-ini     # Provide information about apio.ini
"""


@click.command(
    name="apio.ini",
    short_help="Project file apio.ini documentation.",
    help=APIO_DOCS_RESOURCES_HELP,
)
def cli():
    """Implements the 'apio docs apio-ini' command."""

    console = Console(width=70)

    console.rule(style="blue")
    for option, text in project.OPTIONS.items():
        is_required = option in project.REQUIRED_OPTIONS
        req = "REQUIRED" if is_required else "OPTIONAL"
        console.print(f"\n[magenta]{option.upper()}[/magenta] ({req})")
        console.print(text)
        console.rule(style="blue")

        # print(console.render(val).)
