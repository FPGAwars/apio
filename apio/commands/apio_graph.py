# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio graph' command"""

import sys
from pathlib import Path
import click
from apio.managers.scons import SCons
from apio.utils import cmd_util
from apio.commands import options
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils.util import nameof


# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------


pdf_option = click.option(
    "pdf",  # Var name.
    "--pdf",
    is_flag=True,
    help="Generate a pdf file.",
    cls=cmd_util.ApioOption,
)

png_option = click.option(
    "png",  # Var name.
    "--png",
    is_flag=True,
    help="Generate a png file.",
    cls=cmd_util.ApioOption,
)


# ---------------------------
# -- COMMAND
# ---------------------------
APIO_GRAPH_HELP = """
The command ‘apio graph’ generates a graphical representation of the Verilog
code in the project.

\b
Examples:
  apio graph               # Generate a svg file.
  apio graph --pdf         # Generate a pdf file.
  apio graph --png         # Generate a png file.
  apio graph -t my_module  # Graph my_module module.


[Hint] On Windows, type ‘explorer _build/hardware.svg’ to view the graph,
and on Mac OS type ‘open _build/hardware.svg’.
"""


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
@click.command(
    name="graph",
    short_help="Generate a visual graph of the code.",
    help=APIO_GRAPH_HELP,
)
@click.pass_context
@pdf_option
@png_option
@options.project_dir_option
@options.top_module_option_gen(help="Set the name of the top module to graph.")
@options.verbose_option
def cli(
    cmd_ctx: click.Context,
    # Options
    pdf: bool,
    png: bool,
    project_dir: Path,
    verbose: bool,
    top_module: str,
):
    """Implements the apio graph command."""
    # -- Sanity check the options.
    cmd_util.check_at_most_one_param(cmd_ctx, nameof(pdf, png))

    # -- Construct the graph spec to pass to scons.
    # -- For now it's trivial.
    if pdf:
        graph_spec = "pdf"
    elif png:
        graph_spec = "png"
    else:
        graph_spec = "svg"

    # -- Create the apio context.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_REQUIRED, project_dir_arg=project_dir
    )

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # -- Graph the project with the given parameters
    exit_code = scons.graph(
        {
            "top-module": top_module,
            "graph_spec": graph_spec,
            "verbose_all": verbose,
        }
    )

    # -- Done!
    sys.exit(exit_code)
