# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import sys
import click

from apio.managers.scons import SCons

# Python3 compat
if sys.version_info > (3, 0):
    unicode = str


@click.command("clean")
@click.pass_context
@click.option(
    "-p",
    "--project-dir",
    type=unicode,
    metavar="path",
    help="Set the target directory for the project.",
)
@click.option(
    "-b", "--board", type=unicode, metavar="board", help="Set the board."
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show the entire output of the command.",
)
def cli(ctx, board, project_dir, verbose):
    """Clean the previous generated files."""
    exit_code = SCons(project_dir).clean(
        {"board": board, "verbose": {"all": verbose}}
    )
    ctx.exit(exit_code)
