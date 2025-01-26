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
from dataclasses import dataclass
from typing import List, Dict
import click
from apio.utils.apio_console import cout, cstyle
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils import util
from apio.commands import options


# R0801: Similar lines in 2 files
# pylint: disable=R0801
# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class Entry:
    """A class to hold the field of a single line of the report."""

    fpga: str
    board_count: int
    fpga_arch: str
    fpga_part_num: str
    fpga_size: str
    fpga_type: str
    fpga_pack: str
    fpga_speed: str

    def sort_key(self):
        """A key for sorting the fpga entries in our prefered order."""
        return (util.fpga_arch_sort_key(self.fpga_arch), self.fpga.lower())


# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
def list_fpgas(apio_ctx: ApioContext, verbose: bool):
    """Prints all the available FPGA definitions."""

    # -- Get the output info (terminal vs pipe).
    output_config = util.get_terminal_config()

    # -- Collect a sparse dict with fpga ids to board count.
    boards_counts: Dict[str, int] = {}
    for board_info in apio_ctx.boards.values():
        fpga = board_info.get("fpga", None)
        if fpga:
            old_count = boards_counts.get(fpga, 0)
            boards_counts[fpga] = old_count + 1

    # -- Collect all entries.
    entries: List[Entry] = []
    for fpga, fpga_info in apio_ctx.fpgas.items():
        # -- Construct the Entry for this fpga.
        board_count = boards_counts.get(fpga, 0)
        fpga_arch = fpga_info.get("arch", "")
        fpga_part_num = fpga_info.get("part_num", "")
        fpga_size = fpga_info.get("size", "")
        fpga_type = fpga_info.get("type", "")
        fpga_pack = fpga_info.get("pack", "")
        fpga_speed = fpga_info.get("speed", "")
        # -- Append to the list
        entries.append(
            Entry(
                fpga=fpga,
                board_count=board_count,
                fpga_arch=fpga_arch,
                fpga_part_num=fpga_part_num,
                fpga_size=fpga_size,
                fpga_type=fpga_type,
                fpga_pack=fpga_pack,
                fpga_speed=fpga_speed,
            )
        )

    # -- Sort boards by our prefered order.
    entries.sort(key=lambda x: x.sort_key())

    # -- Compute field lengths
    margin = 3
    fpga_len = max(len(x.fpga) for x in entries) + margin
    board_count_len = 6 + margin
    fpga_arch_len = max(len(x.fpga_arch) for x in entries) + margin
    fpga_part_num_len = max(len(x.fpga_part_num) for x in entries) + margin
    fpga_size_len = max(len(x.fpga_size) for x in entries) + margin
    fpga_type_len = max(len(x.fpga_type) for x in entries) + margin
    fpga_pack_len = max(len(x.fpga_pack) for x in entries) + margin
    fpga_speed_len = 5 + margin

    # -- Construct the title fields.
    parts = []
    parts.append(f"{'FPGA-ID':<{fpga_len}}")
    parts.append(f"{'BOARDS':<{board_count_len}}")
    parts.append(f"{'ARCH':<{fpga_arch_len}}")
    parts.append(f"{'PART-NUMBER':<{fpga_part_num_len}}")
    parts.append(f"{'SIZE':<{fpga_size_len}}")
    if verbose:
        parts.append(f"{'TYPE':<{fpga_type_len}}")
        parts.append(f"{'PACK':<{fpga_pack_len}}")
        parts.append(f"{'SPEED':<{fpga_speed_len}}")

    # -- Print the title
    cout("".join(parts), style="cyan")

    # -- Iterate and print the fpga entries in the list.
    last_arch = None
    for entry in entries:
        # -- Seperation before each archictecture group, unless piped out.
        if last_arch != entry.fpga_arch and output_config.terminal_mode:
            cout("")
            cout(f"{entry.fpga_arch.upper()}", style="magenta")
        last_arch = entry.fpga_arch

        # -- Construct the fpga fields.
        parts = []
        parts.append(cstyle(f"{entry.fpga:<{fpga_len}}", style="cyan"))
        board_count = f"{entry.board_count:>3}" if entry.board_count else ""
        parts.append(f"{board_count:<{board_count_len}}")
        parts.append(f"{entry.fpga_arch:<{fpga_arch_len}}")
        parts.append(f"{entry.fpga_part_num:<{fpga_part_num_len}}")
        parts.append(f"{entry.fpga_size:<{fpga_size_len}}")
        if verbose:
            parts.append(f"{entry.fpga_type:<{fpga_type_len}}")
            parts.append(f"{entry.fpga_pack:<{fpga_pack_len}}")
            parts.append(f"{entry.fpga_speed:<{fpga_speed_len}}")

        # -- Print the fpga line.
        cout("".join(parts))

    # -- Show summary.
    if output_config.terminal_mode:
        cout(f"Total of {util.plurality(entries, 'fpga')}")
        if not verbose:
            cout("Run 'apio fpgas -v' for additional columns.", style="yellow")


# ---------------------------
# -- COMMAND
# ---------------------------
# R0801: Similar lines in 2 files
# pylint: disable = R0801
APIO_FPGAS_HELP = """
The command ‘apio fpgas’ lists the FPGAs recognized by Apio. Custom FPGAs
supported by the underlying Yosys toolchain can be defined by placing a
custom fpgas.jsonc file in the project directory, overriding Apio’s standard
fpgas.jsonc file.

\b
Examples:
  apio fpgas               # List all fpgas.
  apio fpgas -v            # List with extra columns.
  apio fpgas | grep gowin  # Filter FPGA results.

"""


@click.command(
    name="fpgas",
    short_help="List available FPGA definitions.",
    help=APIO_FPGAS_HELP,
)
@options.verbose_option
@options.project_dir_option
def cli(
    # Options
    verbose: bool,
    project_dir: Path,
):
    """Implements the 'fpgas' command which lists available fpga
    definitions.
    """

    # -- Create the apio context. If project dir has a fpgas.jsonc file,
    # -- it will be loaded instead of the apio's standard file.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_OPTIONAL, project_dir_arg=project_dir
    )

    list_fpgas(apio_ctx, verbose)
    sys.exit(0)
