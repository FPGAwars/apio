# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio graph' command"""

import sys
from typing import Optional
from pathlib import Path
import click
from apio.managers.scons_manager import SConsManager
from apio.commands import options
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.utils import cmd_util
from apio.common.proto.apio_pb2 import GraphOutputType, GraphParams, Verbosity


# ---------- apio graph

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

no_viewer_option = click.option(
    "no_viewer",  # Var name.
    "-n",
    "--no-viewer",
    is_flag=True,
    help="Do not open graph viewer.",
    cls=cmd_util.ApioOption,
)

# -- Text in the rich-text format of the python rich library.
APIO_GRAPH_HELP = """
The command 'apio graph' generates a graphical representation of the design \
and then opens it in a graphical viewer.

Examples:[code]
  apio graph               # Generate a svg file (default).
  apio graph --no-viewer   # Suppress the graphical viewer.
  apio graph --svg         # Generate a svg file.
  apio graph --pdf         # Generate a pdf file.
  apio graph --png         # Generate a png file.
  apio graph -t my_module  # Graph my_module module.[/code]


[b][Hint][/b] On Windows, type 'explorer _build/default/graph.svg' to view \
the graph, and on Mac OS type 'open _build/default/graph.svg' (if your \
env is different than 'default' change the commands accordingly).
"""


@click.command(
    name="graph",
    cls=cmd_util.ApioCommand,
    short_help="Generate a visual graph of the code.",
    help=APIO_GRAPH_HELP,
)
@click.pass_context
@svg_option
@png_option
@pdf_option
@options.env_option_gen()
@options.project_dir_option
@options.top_module_option_gen(
    short_help="Set the name of the top module to graph."
)
@no_viewer_option
@options.verbose_option
def cli(
    cmd_ctx: click.Context,
    # Options
    svg: bool,
    png: bool,
    pdf: bool,
    env: Optional[str],
    project_dir: Optional[Path],
    top_module: str,
    no_viewer: bool,
    verbose: bool,
):
    """Implements the apio graph command."""

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments

    # -- Make pylint happy.
    _ = (svg,)

    # -- Sanity check the options.
    cmd_util.check_at_most_one_param(cmd_ctx, ["svg", "png", "pdf"])

    # -- Create the apio context.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.PROJECT_REQUIRED,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        project_dir_arg=project_dir,
        env_arg=env,
    )

    # -- Create the scons manager.
    scons = SConsManager(apio_ctx)

    # -- Determine the output type.
    if pdf:
        output_type = GraphOutputType.PDF
    elif png:
        output_type = GraphOutputType.PNG
    else:
        output_type = GraphOutputType.SVG

    # -- Construct the command info.
    graph_params = GraphParams(
        output_type=output_type,
        open_viewer=not no_viewer,
    )
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
