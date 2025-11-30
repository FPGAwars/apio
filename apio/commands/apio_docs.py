# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio format' command"""

import sys
import webbrowser
import click
from apio.common.apio_console import cout
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.utils import cmd_util


# -------------- apio format

# -- Text in the rich-text format of the python rich library.
APIO_DOCS_HELP = """
The command 'apio docs' opens the Apio documentation using the user's \
default browser.

Examples:[code]
  apio docs              # Open the apio docs.
  apio docs --commands   # Land on the commands list page.
"""

commands_option = click.option(
    "commands",  # Var name.
    "-c",
    "--commands",
    is_flag=True,
    help="Show the commands page.",
    cls=cmd_util.ApioOption,
)


@click.command(
    name="docs",
    cls=cmd_util.ApioCommand,
    short_help="Show Apio documentation.",
    help=APIO_DOCS_HELP,
)
@commands_option
def cli(
    # Options
    commands,
):
    """Implements the docs command which opens the apio documentation in
    the default browser.
    """

    # -- Create an apio context with a project object.
    _ = ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.IGNORE_PACKAGES,
    )

    url = "https://fpgawars.github.io/apio/docs"

    if commands:
        url += "/commands-list"

    cout(f"URL: {url}")
    cout("Opening default browser")

    default_browser = webbrowser.get()
    default_browser.open(url)

    sys.exit(0)
