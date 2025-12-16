# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio examples' command"""

import sys
import re
from datetime import date
from pathlib import Path
from typing import List, Any, Optional
import click
from rich.table import Table
from rich import box
from apio.common.apio_console import cerror
from apio.common import apio_console
from apio.common.apio_console import cout, ctable, cwrite
from apio.common.apio_styles import INFO, BORDER, EMPH1
from apio.managers.examples import Examples, ExampleInfo
from apio.commands import options
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.utils import util
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand


# ---- apio examples list


# -- Text in the rich-text format of the python rich library.
APIO_EXAMPLES_LIST_HELP = """
The command 'apio examples list' lists the available Apio project examples \
that you can use.

Examples:[code]
  apio examples list                     # List all examples
  apio examples list  -v                 # More verbose output.
  apio examples list | grep alhambra-ii  # Show alhambra-ii examples.
  apio examples list | grep -i blink     # Show blinking examples.
  apio examples list --docs              # Use Apio docs format.[/code]
"""


def examples_sort_key(entry: ExampleInfo) -> Any:
    """A key for sorting the fpga entries in our preferred order."""
    return (util.fpga_arch_sort_key(entry.fpga_arch), entry.name)


def list_examples(apio_ctx: ApioContext, verbose: bool) -> None:
    """Print all the examples available. Return a process exit
    code, 0 if ok, non zero otherwise."""

    # -- Get list of examples.
    entries: List[ExampleInfo] = Examples(apio_ctx).get_examples_infos()

    # -- Sort boards by case insensitive board id.
    entries.sort(key=examples_sort_key)

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=False,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio Examples",
        title_justify="left",
    )

    # -- Add columns.
    table.add_column("BOARD/EXAMPLE", no_wrap=True, style=EMPH1)
    table.add_column("ARCH", no_wrap=True)
    if verbose:
        table.add_column("PART-NUM", no_wrap=True)
        table.add_column("SIZE", no_wrap=True)
    table.add_column(
        "DESCRIPTION",
        no_wrap=True,
        max_width=40 if verbose else 70,  # Limit in verbose mode.
    )

    # -- Add rows.
    last_arch = None
    for entry in entries:
        # -- Separation before each architecture group, unless piped out.
        if last_arch != entry.fpga_arch and apio_console.is_terminal():
            table.add_section()
        last_arch = entry.fpga_arch

        # -- Collect row's values.
        values = []
        values.append(entry.name)
        values.append(entry.fpga_arch)
        if verbose:
            values.append(entry.fpga_part_num)
            values.append(entry.fpga_size)
        values.append(entry.description)

        # -- Append the row
        table.add_row(*values)

    # -- Render the table.
    cout()
    ctable(table)

    # -- Print summary.
    if apio_console.is_terminal():
        cout(f"Total of {util.plurality(entries, 'example')}")
        if not verbose:
            cout(
                "Run 'apio examples list -v' for additional columns.",
                style=INFO,
            )


def list_examples_docs_format(apio_ctx: ApioContext):
    """Output examples information in a format for Apio Docs."""

    # -- Get the version of the 'definitions' package use. At this point it's
    # -- expected to be installed.
    def_version, _ = apio_ctx.profile.get_installed_package_info("definitions")

    # -- Get list of examples.
    entries: List[ExampleInfo] = Examples(apio_ctx).get_examples_infos()

    # -- Sort boards by case insensitive board id.
    entries.sort(key=examples_sort_key)

    # -- Determine column sizes
    w1 = max(len("EXAMPLE"), *(len(entry.name) for entry in entries))
    w2 = max(
        len("DESCRIPTION"),
        *(len(entry.description) for entry in entries),
    )

    # -- Print page header
    today = date.today()
    today_str = f"{today.strftime('%B')} {today.day}, {today.year}"
    cwrite("\n<!-- BEGIN generation by 'apio examples list --docs' -->\n")
    cwrite("\n# Apio Examples\n")
    cwrite(
        f"\nThis markdown page was generated automatically on {today_str} "
        f"from version `{def_version}` of the Apio definitions package.\n"
    )
    cwrite(
        "\n> Apio project examples can be submitted to the "
        "[apio-examples](https://github.com/FPGAwars/apio-examples) Github "
        "repository.\n"
    )

    # -- Add the rows, with separation line between architecture groups.
    last_arch = None
    for entry in entries:
        # -- If switching architecture, add an horizontal separation line.
        if last_arch != entry.fpga_arch:

            cout(f"\n## {entry.fpga_arch.upper()} examples")

            cwrite(
                "\n| {0} | {1} |\n".format(
                    "EXAMPLE".ljust(w1),
                    "DESCRIPTION".ljust(w2),
                )
            )
            cwrite(
                "| {0} | {1} |\n".format(
                    ":-".ljust(w1, "-"),
                    ":-".ljust(w2, "-"),
                )
            )

            last_arch = entry.fpga_arch

        # -- Write the entry
        cwrite(
            "| {0} | {1} |\n".format(
                entry.name.ljust(w1),
                entry.description.ljust(w2),
            )
        )

    cwrite("\n<!-- END generation by 'apio examples list --docs' -->\n\n")


@click.command(
    name="list",
    cls=ApioCommand,
    short_help="List the available apio examples.",
    help=APIO_EXAMPLES_LIST_HELP,
)
@options.docs_format_option
@options.verbose_option
def _list_cli(docs: bool, verbose: bool):
    """Implements the 'apio examples list' command group."""

    # -- Create the apio context.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
    )

    # -- List the examples.
    if docs:
        list_examples_docs_format(apio_ctx)
    else:
        list_examples(apio_ctx, verbose)


# ---- apio examples fetch

# -- Text in the rich-text format of the python rich library.
APIO_EXAMPLES_FETCH_HELP = """
The command 'apio examples fetch' fetches a single examples or all the \
examples of a board. The destination directory is either the current \
directory or the directory specified with '--dst' and it should be empty \
and non existing.

Examples:[code]
  apio examples fetch alhambra-ii/ledon    # Single example
  apio examples fetch alhambra-ii          # All board's examples
  apio examples fetch alhambra-ii -d work  # Explicit destination

"""


@click.command(
    name="fetch",
    cls=ApioCommand,
    short_help="Fetch the files of an example.",
    help=APIO_EXAMPLES_FETCH_HELP,
)
@click.argument("example", metavar="EXAMPLE", nargs=1, required=True)
@options.dst_option_gen(short_help="Set a different destination directory.")
def _fetch_cli(
    # Arguments
    example: str,
    # Options
    dst: Optional[Path],
):
    """Implements the 'apio examples fetch' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
    )

    # -- Create the examples manager.
    examples = Examples(apio_ctx)

    # -- Determine the destination directory.
    dst_dir_path = util.user_directory_or_cwd(
        dst, description="Destination", must_exist=False
    )

    # Parse the argument as board or board/example
    pattern = r"^([a-zA-Z0-9-]+)(?:[/]([a-zA-Z0-9-]+))?$"
    match = re.match(pattern, example)
    if not match:
        cerror(f"Invalid example specification '{example}.")
        cout(
            "Expecting board-id or board/example-name, e.g. "
            "'alhambra-ii' or 'alhambra-ii/blinky.",
            style=INFO,
        )
        sys.exit(1)
    board_id: str = match.group(1)
    example_name: Optional[str] = match.group(2)

    if example_name:
        # -- Copy the files of a single example.
        examples.copy_example_files(example, dst_dir_path)
    else:
        # -- Copy the directories of the board's examples.
        examples.copy_board_examples(board_id, dst_dir_path)


# ---- apio examples

# -- Text in the rich-text format of the python rich library.
APIO_EXAMPLES_HELP = """
The command group 'apio examples' provides subcommands for listing and \
fetching Apio provided examples. Each example is a self contained \
mini project that can be built and uploaded to an FPGA board.
"""


# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _list_cli,
            _fetch_cli,
        ],
    )
]


@click.command(
    name="examples",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="List and fetch apio examples.",
    help=APIO_EXAMPLES_HELP,
)
def cli():
    """Implements the 'apio examples' command group."""

    # pass
