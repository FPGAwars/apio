# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio fpgas' command"""

import sys
from pathlib import Path
import click
from apio.apio_context import ApioContext
from apio import cmd_util, util
from apio.commands import options


def list_fpgas(apio_ctx: ApioContext):
    """Prints all the available FPGA definitions."""

    # Get terminal configuration. It will help us to adapt the format
    # to a terminal vs a pipe.
    config: util.TerminalConfig = util.get_terminal_config()

    if config.terminal_mode():
        # -- Horizontal line across the terminal,
        seperator_line = "─" * config.terminal_width

        # -- Table title
        fpga_header = click.style(f"{'  FPGA':34}", fg="cyan")
        title = (
            f"{fpga_header} {'Arch':<10} {'Type':<13}" f" {'Size':<8} {'Pack'}"
        )

        # -- Print the table header
        click.secho(seperator_line)
        click.secho(title)
        click.secho(seperator_line)

    # -- Print all the fpgas!
    for fpga in apio_ctx.fpgas:

        # -- Get information about the FPGA
        arch = apio_ctx.fpgas[fpga]["arch"]
        _type = apio_ctx.fpgas[fpga]["type"]
        size = apio_ctx.fpgas[fpga]["size"]
        pack = apio_ctx.fpgas[fpga]["pack"]

        # -- Print the item with information
        data_str = f"{arch:<10} {_type:<13} {size:<8} {pack}"
        if config.terminal_mode():
            # -- For terminal, print the FPGA name in color.
            fpga_str = click.style(f"{fpga:32}", fg="cyan")
            item = f"{fpga_str} {data_str}"
            click.secho(item)
        else:
            # -- For pipe, no colors and no bullet point.
            click.secho(f"{fpga:32} {data_str}")

    # -- Print the Footer
    if config.terminal_mode():
        click.secho(seperator_line)

    click.secho(f"Total of {util.plurality(apio_ctx.fpgas, 'fpga')}")


# ---------------------------
# -- COMMAND
# ---------------------------
# R0801: Similar lines in 2 files
# pylint: disable = R0801
HELP = """
The fpgas commands lists the FPGA that are recongnized by apio.
Custom FPGAS that are supported by the underlying Yosys tools chain can be
defined by placing a custom fpgas.json file in the
project directory. If such a case, the command
lists the fpgas from that custom file.
The commands is typically used in the root directory
of the project that contains the apio.ini file.

\b
Examples:
  apio fpgas               # List all fpgas
  apio fpgas | grep gowin  # Filter FPGA results.

"""


@click.command(
    "fpgas",
    short_help="List available FPGA definitions.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.project_dir_option
def cli(
    _: click.core.Context,
    # Options
    project_dir: Path,
):
    """Implements the 'fpgas' command which lists available fpga
    definitions.
    """

    # -- Create the apio context. If project dir has a fpgas.json file,
    # -- it will be loaded instead of the apio's standard file.
    apio_ctx = ApioContext(project_dir=project_dir, load_project=False)

    list_fpgas(apio_ctx)
    sys.exit(0)
