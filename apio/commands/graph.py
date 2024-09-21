# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO GRAPH command"""

from pathlib import Path
import click
from click.core import Context
from apio.managers.scons import SCons
from apio import util
from apio.commands import options


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The graph command generates a graphical representation of the
verilog code in the project.
The commands is typically used in the root directory
of the project that contains the apio.ini file.

\b
Examples:
  apio graph

The graph command generates the graph in .dot format and then invokes
the dot command from the path to convert it to a .svg format. The dot
command is not included with the apio distribution and needed to be
installed seperatly. See https://graphviz.org for more details.

[Hint] If you need the graph in other formats, convert the .dot file
to the desired format using the dot command.
"""


@click.command(
    "graph",
    short_help="Generate a visual graph of the code.",
    help=HELP,
    context_settings=util.context_settings(),
)
@click.pass_context
@options.project_dir_option
@options.top_module_option_gen()
@options.verbose_option
def cli(
    ctx: Context,
    # Options
    project_dir: Path,
    verbose: bool,
    top_module: str,
):
    """Implements the apio graph command."""

    # -- Crete the scons object
    scons = SCons(project_dir)

    # -- Graph the project with the given parameters
    exit_code = scons.graph(
        {
            "verbose": {"all": verbose, "yosys": False, "pnr": False},
            "top-module": top_module,
        }
    )

    # -- Done!
    ctx.exit(exit_code)
