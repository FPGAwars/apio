# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Authors Jesús Arroyo, Miodrag Milanovic
# -- Licence GPLv2
"""TODO"""

import click

from apio.managers.scons import SCons


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
# pylint: disable=W0622
@click.command("lint")
@click.pass_context
@click.option(
    "-a",
    "--all",
    is_flag=True,
    help="Enable all warnings, including code style warnings.",
)
@click.option("-t", "--top", type=str, metavar="top", help="Set top module.")
@click.option("--nostyle", is_flag=True, help="Disable all style warnings.")
@click.option(
    "--nowarn",
    type=str,
    metavar="nowarn",
    help="Disable specific warning(s).",
)
@click.option(
    "--warn", type=str, metavar="warn", help="Enable specific warning(s)."
)
@click.option(
    "-p",
    "--project-dir",
    type=str,
    metavar="path",
    help="Set the target directory for the project.",
)
def cli(ctx, all, top, nostyle, nowarn, warn, project_dir):
    """Lint the verilog code."""

    exit_code = SCons(project_dir).lint(
        {
            "all": all,
            "top": top,
            "nostyle": nostyle,
            "nowarn": nowarn,
            "warn": warn,
        }
    )
    ctx.exit(exit_code)
