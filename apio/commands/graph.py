# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio graph' command"""

from pathlib import Path
import click
from click.core import Context
from apio.managers.scons import SCons
from apio import cmd_util
from apio.commands import options
from apio.resources import Resources


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
  apio graph               # Graph the top module
  apio graph -t my_module  # Graph the selected module

The graph command generates the graph in .dot format and then invokes
the dot command from the path to convert it to a .svg format. The dot
command is not included with the apio distribution and needed to be
installed seperatly. See https://graphviz.org for more details.

[Hint] If you need the graph in other formats, convert the .dot file
to the desired format using the dot command.
"""

DOT_HELP = """
The 'dot' command is part of the 'graphviz' suite. Please install
it per the instructions at https://graphviz.org/download and run
this command again. If you think that the 'dot' command is available
on the system path, you can try supressing this error message by
adding the --force flag to the apio graph command.
"""


@click.command(
    "graph",
    short_help="Generate a visual graph of the code.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.project_dir_option
@options.top_module_option_gen(help="Set the name of the top module to graph.")
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
    resources = Resources(project_dir=project_dir)
    scons = SCons(resources)

    # -- Graph the project with the given parameters
    exit_code = scons.graph(
        {
            "verbose": {"all": verbose, "yosys": False, "pnr": False},
            "top-module": top_module,
        }
    )

    # -- Done!
    ctx.exit(exit_code)
