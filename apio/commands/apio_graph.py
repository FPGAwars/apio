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
from apio.common.proto.apio_pb2 import GraphOutputType, GraphParams, Verbosity


# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------

svg_option = click.option(
    "svg",  # Var name.
    "--svg",
    is_flag=True,
    help="Generate a svg file (default).",
    cls=cmd_util.ApioOption,
)

png_option = click.option(
    "png",  # Var name.
    "--png",
    is_flag=True,
    help="Generate a png file.",
    cls=cmd_util.ApioOption,
)

pdf_option = click.option(
    "pdf",  # Var name.
    "--pdf",
    is_flag=True,
    help="Generate a pdf file.",
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
  apio graph --svg         # Generate a svg file.
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
@svg_option
@png_option
@pdf_option
@options.project_dir_option
@options.top_module_option_gen(help="Set the name of the top module to graph.")
@options.verbose_option
def cli(
    cmd_ctx: click.Context,
    # Options
    svg: bool,
    png: bool,
    pdf: bool,
    project_dir: Path,
    verbose: bool,
    top_module: str,
):
    """Implements the apio graph command."""
    # -- Sanity check the options.
    cmd_util.check_at_most_one_param(cmd_ctx, nameof(svg, png, pdf))

    # -- Create the apio context.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_REQUIRED, project_dir_arg=project_dir
    )

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # -- Determine the output type.
    if pdf:
        output_type = GraphOutputType.PDF
    elif png:
        output_type = GraphOutputType.PNG
    else:
        output_type = GraphOutputType.SVG

    # -- Construct the command info.
    graph_params = GraphParams(output_type=output_type)
    if top_module:
        graph_params.top_module = top_module

    # -- Construct the verbosity
    verbosity = Verbosity(all=verbose)

    # -- Graph the project with the given parameters
    exit_code = scons.graph(
        graph_params,
        verbosity,
    )

    # -- Done!
    sys.exit(exit_code)
