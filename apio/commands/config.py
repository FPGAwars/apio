# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Main implementation of APIO config command"""

import click

from apio.profile import Profile
from apio import util


@click.command("config", context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-l",
    "--list",
    "_list",
    is_flag=True,
    help="List all configuration parameters.",
)
@click.option(
    "-v",
    "--verbose",
    type=click.Choice(["0", "1"]),
    help="Verbose mode: `0` General, `1` Information.",
)
@click.option(
    "-e",
    "--exe",
    type=click.Choice(["default", "native"]),
    help="Configure executables: `default` selects apio packages, "
    + "`native` selects system binaries.",
)
def cli(ctx, _list, verbose, exe):
    """Apio configuration."""

    # -- Access to the profile file
    profile = Profile()

    # -- List configuration parameters
    if _list:
        profile.list()

    # -- Configure verbose mode
    elif verbose:
        profile.add_config("verbose", verbose)

    # -- Configure executable mode
    elif exe:
        profile.add_config("exe", exe)

    # -- No paratemers: Show the help
    else:
        click.secho(ctx.get_help())
