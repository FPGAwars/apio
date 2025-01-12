# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio boards' command"""

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List
import click
from click import secho, style
from apio.apio_context import ApioContext, ApioContextScope
from apio import util
from apio.commands import options


# R0801: Similar lines in 2 files
# pylint: disable=R0801
# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class Entry:
    """Holds the values of a single board report line."""

    board: str
    board_description: str
    fpga: str
    programmer: str
    fpga_arch: str
    fpga_part_num: str
    fpga_size: str
    fpga_type: str
    fpga_pack: str

    def sort_key(self):
        """Returns a key for sorting entiries. Primary key is the architecture
        by our prefered order, secondary key is board id."""
        # -- Prefer arch order
        archs = ["ice40", "ecp5", "gowin"]
        # -- Primary key
        primary_key = (
            archs.index(self.fpga_arch)
            if self.fpga_arch in archs
            else len(archs)
        )
        # -- Secondary key is board name.
        return (primary_key, self.board.lower())


# R0914: Too many local variables (17/15)
# pylint: disable=R0914
# pylint: disable=too-many-statements
def list_boards(apio_ctx: ApioContext, verbose: bool):
    """Prints all the available board definitions."""

    # -- Collect the boards info into a list of entires, one per board.
    entries: List[Entry] = []
    for board, board_info in apio_ctx.boards.items():
        board_description = board_info.get("description", "")
        programmer = board_info.get("programmer", {}).get("type", "")
        fpga = board_info.get("fpga", "")
        fpga_info = apio_ctx.fpgas.get(fpga, {})
        fpga_arch = fpga_info.get("arch", "")
        fpga_part_num = fpga_info.get("part_num", "")
        fpga_size = fpga_info.get("size", "")
        fpga_type = fpga_info.get("type", "")
        fpga_pack = fpga_info.get("pack", "")
        entries.append(
            Entry(
                board,
                board_description,
                fpga,
                programmer,
                fpga_arch,
                fpga_part_num,
                fpga_size,
                fpga_type,
                fpga_pack,
            )
        )

    # -- Sort boards by case insensitive board namd.
    entries.sort(key=lambda x: x.sort_key())

    # -- Compute the columns widths.
    margin = 4
    board_len = max(len(x.board) for x in entries) + margin
    board_description_len = (
        max(len(x.board_description) for x in entries) + margin
    )
    fpga_len = max(len(x.fpga) for x in entries) + margin
    programmer_len = max(len(x.programmer) for x in entries) + margin
    fpga_arch_len = max(len(x.fpga_arch) for x in entries) + margin
    fpga_part_num_len = max(len(x.fpga_part_num) for x in entries) + margin
    fpga_type_len = max(len(x.fpga_type) for x in entries) + margin
    fpga_size_len = max(len(x.fpga_size) for x in entries) + margin
    fpga_pack_len = max(len(x.fpga_pack) for x in entries) + margin

    # -- Construct the title fields.
    parts = []
    parts.append(f"{'BOARD':<{board_len}}")
    if verbose:
        parts.append(f"{'DESCRIPTION':<{board_description_len}}")
    parts.append(f"{'ARCH':<{fpga_arch_len}}")
    if verbose:
        parts.append(f"{'FPGA':<{fpga_len}}")
    parts.append(f"{'PART NUMBER':<{fpga_part_num_len}}")
    if verbose:
        parts.append(f"{'TYPE':<{fpga_type_len}}")
    parts.append(f"{'SIZE':<{fpga_size_len}}")
    if verbose:
        parts.append(f"{'PACK':<{fpga_pack_len}}")
    parts.append(f"{'PROGRAMMER':<{programmer_len}}")

    # -- Show the title line.
    secho("".join(parts), fg="cyan", bold=True)

    # -- Print all the boards!
    for x in entries:

        # -- Construct the line fields.
        parts = []
        parts.append(style(f"{x.board:<{board_len}}", fg="cyan"))
        if verbose:
            parts.append(f"{x.board_description:<{board_description_len}}")
        parts.append(f"{x.fpga_arch:<{fpga_arch_len}}")
        if verbose:
            parts.append(f"{x.fpga:<{fpga_len}}")
        parts.append(f"{x.fpga_part_num:<{fpga_part_num_len}}")
        if verbose:
            parts.append(f"{x.fpga_type:<{fpga_type_len}}")
        parts.append(f"{x.fpga_size:<{fpga_size_len}}")
        if verbose:
            parts.append(f"{x.fpga_pack:<{fpga_pack_len}}")
        parts.append(f"{x.programmer:<{programmer_len}}")

        # -- Print the line
        secho("".join(parts))

    # -- Show the summary.

    secho(f"Total of {util.plurality(entries, 'board')}")
    if not verbose:
        secho("Run 'apio boards -v' for additional columns.", fg="yellow")


# ---------------------------
# -- COMMAND
# ---------------------------
# R0801: Similar lines in 2 files
# pylint: disable = R0801
APIO_BOARDS_HELP = """
The command 'apio boards' lists the FPGA boards recognized by Apio.
Custom boards can be defined by placing a custom 'boards.json' file in the
project directory, which will override Apio’s default 'boards.json' file.

\b
Examples:
  apio boards                   # List all boards.
  apio boards -v                # List with extra columns..
  apio boards | grep ecp5       # Filter boards results.

"""


@click.command(
    name="boards",
    short_help="List available board definitions.",
    help=APIO_BOARDS_HELP,
)
@options.verbose_option
@options.project_dir_option
def cli(
    # Options
    verbose: bool,
    project_dir: Path,
):
    """Implements the 'boards' command which lists available board
    definitions."""

    # -- Create the apio context. If the project exists, it's custom
    # -- boards.json is also loaded.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_OPTIONAL,
        project_dir_arg=project_dir,
    )

    list_boards(apio_ctx, verbose)
    sys.exit(0)
