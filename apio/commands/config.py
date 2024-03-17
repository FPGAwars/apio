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

# ------------------
# -- CONSTANTS
# ------------------
CMD = "config"  # -- Comand name
LIST = "list"  # -- Option
VERBOSE = "verbose"  # -- Option
EXE = "exe"  # -- Option


@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-l",
    f"--{LIST}",
    is_flag=True,
    help="List all configuration parameters.",
)
@click.option(
    "-v",
    f"--{VERBOSE}",
    type=click.Choice(["0", "1"]),
    help="Verbose mode: `0` General, `1` Information.",
)
@click.option(
    "-e",
    f"--{EXE}",
    type=click.Choice(["default", "native"]),
    help="Configure executables: `default` selects apio packages, "
    + "`native` selects system binaries.",
)
def cli(ctx, **kwargs):
    """Apio configuration."""

    # -- Extract the arguments
    _list = kwargs[LIST]
    verbose = kwargs[VERBOSE]
    exe = kwargs[EXE]

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
