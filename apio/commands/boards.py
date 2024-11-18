# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio boards' command"""

from pathlib import Path
from varname import nameof
import click
from apio.resources import ApioContext
from apio import cmd_util
from apio.commands import options

# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
list_fpgas_option = click.option(
    "fpgas",  # Var name
    "-f",
    "--fpga",
    is_flag=True,
    help="List supported FPGA chips.",
    cls=cmd_util.ApioOption,
)


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The boards commands lists the FPGA boards and chips that are
supported by apio.
The commands is typically used in the root directory
of the project that contains the apio.ini file.

\b
Examples:
  apio boards --list           # List boards
  apio boards --fpga           # List FPGAs
  apio boards -l | grep ecp5   # Filter boards results
  apio boards -f | grep gowin  # Filter FPGA results.

[Advanced] Boards with wide availability can be added by contacting the
apio team. Custom one-of boards can be added to your project by
placing an alternative boards.json file in your apio project directory.
"""


@click.command(
    "boards",
    short_help="List supported boards and FPGAs.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.project_dir_option
@options.list_option_gen(help="List supported FPGA boards.")
@list_fpgas_option
def cli(
    cmd_ctx: click.core.Context,
    # Options
    project_dir: Path,
    list_: bool,
    fpgas: bool,
):
    """Implements the 'boards' command which lists supported boards
    and FPGAs.
    """

    # Make sure these params are exclusive.
    cmd_util.check_at_most_one_param(cmd_ctx, nameof(list_, fpgas))

    # -- Create an apio context. We need project scope since the project
    # -- may override the list of boards.
    apio_ctx = ApioContext(project_dir=project_dir, project_scope=True)

    # -- Option 1: List boards
    if list_:
        apio_ctx.list_boards()
        cmd_ctx.exit(0)

    # -- Option 2: List fpgas
    if fpgas:
        apio_ctx.list_fpgas()
        cmd_ctx.exit(0)

    # -- No options: show help
    click.secho(cmd_ctx.get_help())
