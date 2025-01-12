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
from typing import List
import click
from click import secho, style, echo
from apio.apio_context import ApioContext, ApioContextScope
from apio import util
from apio.commands import options


# R0801: Similar lines in 2 files
# pylint: disable=R0801
@dataclass(frozen=True)
class Entry:
    """A class to hold the field of a single line of the report."""

    fpga: str
    fpga_arch: str
    fpga_part_num: str
    fpga_size: str
    fpga_type: str
    fpga_pack: str

    def sort_key(self):
        """A kery for sorting entries. Primary key is architecture, by
        our prefer order, and secondary is fpga id."""
        # -- Prefer arch order
        archs = ["ice40", "ecp5", "gowin"]
        # -- Primary key
        primary_key = (
            archs.index(self.fpga_arch)
            if self.fpga_arch in archs
            else len(archs)
        )
        # -- Secondary key is board name.
        return (primary_key, self.fpga.lower())


# pylint: disable=too-many-locals
def list_fpgas(apio_ctx: ApioContext, verbose: bool):
    """Prints all the available FPGA definitions."""

    # -- Collect all entries.
    entries: List[Entry] = []
    for fpga, fpga_info in apio_ctx.fpgas.items():
        # -- Construct the Entry for this fpga.
        fpga_arch = fpga_info.get("arch", "")
        fpga_part_no = fpga_info.get("model", "")
        fpga_size = fpga_info.get("size", "")
        fpga_type = fpga_info.get("type", "")
        fpga_pack = fpga_info.get("pack", "")
        # -- Append to the list
        entries.append(
            Entry(
                fpga,
                fpga_arch,
                fpga_part_no,
                fpga_size,
                fpga_type,
                fpga_pack,
            )
        )

    # -- Sort boards by case insensitive board namd.
    entries.sort(key=lambda x: x.sort_key())

    # -- Compute field lengths
    margin = 4
    fpga_len = max(len(x.fpga) for x in entries) + margin
    fpga_arch_len = max(len(x.fpga_arch) for x in entries) + margin
    fpga_part_num_len = max(len(x.fpga_part_num) for x in entries) + margin
    fpga_size_len = max(len(x.fpga_size) for x in entries) + margin
    fpga_type_len = max(len(x.fpga_type) for x in entries) + margin
    fpga_pack_len = max(len(x.fpga_pack) for x in entries) + margin

    # -- Construct the title fields.
    parts = []
    parts.append(f"{'FPGA ID':<{fpga_len}}")
    parts.append(f"{'AECH':<{fpga_arch_len}}")
    parts.append(f"{'PART NUMBER':<{fpga_part_num_len}}")
    parts.append(f"{'SIZE':<{fpga_size_len}}")
    if verbose:
        parts.append(f"{'TYPE':<{fpga_type_len}}")
        parts.append(f"{'PACKAGE':<{fpga_pack_len}}")

    # -- Print the title
    secho("".join(parts), fg="cyan", bold="True")

    # -- Iterate and print the fpga entries in the list.
    for x in entries:

        # -- Construct the fpga fields.
        parts = []
        parts.append(style(f"{x.fpga:<{fpga_len}}", fg="cyan"))
        parts.append(f"{x.fpga_arch:<{fpga_arch_len}}")
        parts.append(f"{x.fpga_part_num:<{fpga_part_num_len}}")
        parts.append(f"{x.fpga_size:<{fpga_size_len}}")
        if verbose:
            parts.append(f"{x.fpga_type:<{fpga_type_len}}")
            parts.append(f"{x.fpga_pack:<{fpga_pack_len}}")

        # -- Print the fpga line.
        echo("".join(parts))

    # -- Show summary.
    secho(f"Total of {util.plurality(apio_ctx.fpgas, 'fpga')}")
    if not verbose:
        secho("Run 'apio fpgas -v' for additional columns.", fg="yellow")


# ---------------------------
# -- COMMAND
# ---------------------------
# R0801: Similar lines in 2 files
# pylint: disable = R0801
APIO_FPGAS_HELP = """
The command ‘apio fpgas’ lists the FPGAs recognized by Apio. Custom FPGAs
supported by the underlying Yosys toolchain can be defined by placing a
custom fpgas.json file in the project directory, overriding Apio’s standard
fpgas.json file.

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

    # -- Create the apio context. If project dir has a fpgas.json file,
    # -- it will be loaded instead of the apio's standard file.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_OPTIONAL, project_dir_arg=project_dir
    )

    list_fpgas(apio_ctx, verbose)
    sys.exit(0)
