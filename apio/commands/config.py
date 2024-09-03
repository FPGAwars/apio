# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO config command"""

import click
from apio.profile import Profile
from apio import util
from apio.commands import options


# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------


# W0511: TODO
# pylint: disable=W0511
# TODO: Consolidate this numeric option with the shared boolean
# 'verbose' option in options.py.
verbose_option = click.option(
    "verbose",  # Var name
    "-v",
    "--verbose",
    type=click.Choice(["0", "1"]),
    help="Verbose mode: `0` General, `1` Information.",
)


# ---------------------------
# -- COMMAND
# ---------------------------
@click.command("config", context_settings=util.context_settings())
@click.pass_context
@options.list_option_gen(help="List all configuration parameters.")
@verbose_option
def cli(
    ctx,
    # Options
    list_: bool,
    verbose: str,
):
    """Apio configuration."""

    # -- Access to the profile file
    profile = Profile()

    # -- List configuration parameters
    if list_:
        profile.list()

    # -- Configure verbose mode
    elif verbose:
        profile.add_config("verbose", verbose)

    # -- No paratemers: Show the help
    else:
        click.secho(ctx.get_help())
