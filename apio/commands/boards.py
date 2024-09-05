# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO BOARDS command"""

from pathlib import Path
import click
from apio.resources import Resources
from apio import util
from apio.commands import options

# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
list_fpgas_option = click.option(
    "fpgas",  # Var name
    "-f",
    "--fpga",
    is_flag=True,
    help="List all supported FPGA chips.",
)


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The apio boards commands provides information about the FPAG boards that are
supported by apio. To view the list of all supported boards use the command

  apio boards --list

To list the supported FPGAs, replace the --list option with the
--fpga option.

Hint: apio comes with example projects for some boards. See the apio examples
command for more information.

Advanced: Boards with wide availability can be added by contacting the
apio team. You can also add a custon one-of board definition to your apio
project by placing a custom boards.json file in your apio project.
"""


@click.command(
    "boards",
    short_help="List supported boards and FPGAs.",
    help=HELP,
    context_settings=util.context_settings(),
)
@click.pass_context
@options.project_dir_option
@options.list_option_gen(help="List all supported FPGA boards.")
@list_fpgas_option
def cli(
    ctx,
    # Options
    project_dir: Path,
    list_: bool,
    fpgas: bool,
):
    """Implements the 'boards' command which lists supported boards
    and FPGAs.
    """

    # -- Access to the apio resources
    resources = Resources(project_dir=project_dir)

    # -- Option 1: List boards
    if list_:
        resources.list_boards()

    # -- Option 2: List fpgas
    elif fpgas:
        resources.list_fpgas()

    # -- No options: show help
    else:
        click.secho(ctx.get_help())
