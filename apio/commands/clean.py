"""Main implementation of APIO CLEAN command"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

from pathlib import Path

import click

from apio.managers.scons import SCons
from apio import util


@click.command("clean", context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-p",
    "--project-dir",
    type=Path,
    metavar="str",
    help="Set the target directory for the project.",
)
@click.option(
    "-b", "--board", type=str, metavar="str", help="Set the board."
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show the entire output of the command.",
)
def cli(ctx, board, project_dir, verbose):
    """Clean the previous generated files."""

    # -- Create the scons object
    scons = SCons(project_dir)

    # -- Build the project with the given parameters
    exit_code = scons.clean({"board": board, "verbose": {"all": verbose}})

    # -- Done!
    ctx.exit(exit_code)
