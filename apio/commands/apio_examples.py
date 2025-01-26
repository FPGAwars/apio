# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio examples' command"""

from pathlib import Path
from typing import List, Any
import click
from apio.common.apio_console import cout, cstyle
from apio.managers import installer
from apio.managers.examples import Examples, ExampleInfo
from apio.commands import options
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils import util
from apio.utils.cmd_util import ApioGroup, ApioSubgroup


# ---- apio examples list


APIO_EXAMPLES_LIST_HELP = """
The command ‘apio examples list’ lists the available Apio project examples
that you can use.

\b
Examples:
  apio examples list                     # List all examples
  apio examples list  -v                 # List with extra information.
  apio examples list | grep alhambra-ii  # Show examples of a specific board.
  apio examples list | grep -i blink     # Show all blinking examples.

  """


def examples_sort_key(entry: ExampleInfo) -> Any:
    """A key for sorting the fpga entries in our prefered order."""
    return (util.fpga_arch_sort_key(entry.fpga_arch), entry.name)


def list_examples(apio_ctx: ApioContext, verbose: bool) -> None:
    """Print all the examples available. Return a process exit
    code, 0 if ok, non zero otherwise."""
    # -- Get the output info (terminal vs pipe).
    output_config = util.get_terminal_config()

    # -- Make sure that the examples package is installed.
    installer.install_missing_packages_on_the_fly(apio_ctx)

    # -- Get list of examples.
    entries: List[ExampleInfo] = Examples(apio_ctx).get_examples_infos()

    # -- Sort boards by case insensitive board namd.
    entries.sort(key=examples_sort_key)

    # Compute field lengths
    margin = 2
    name_len = max(len(x.name) for x in entries) + margin
    fpga_arch_len = max(len(x.fpga_arch) for x in entries) + margin
    fpga_part_num_len = max(len(x.fpga_part_num) for x in entries) + margin
    fpga_size_len = max(len(x.fpga_size) for x in entries) + margin + 1

    # -- Construct the title fields.
    parts = []
    parts.append(f"{'BOARD/EXAMPLE':<{name_len}}")
    if verbose:
        parts.append(f"{'ARCH':<{fpga_arch_len}}")
        parts.append(f"{'PART-NUM':<{fpga_part_num_len}}")
        parts.append(f"{'SIZE':<{fpga_size_len}}")
    parts.append("DESCRIPTION")

    # -- Print the title
    cout("".join(parts), style="cyan")

    # -- Emit the examples
    last_arch = None
    for entry in entries:
        # -- Seperation before each archictecture group, unless piped out.
        if last_arch != entry.fpga_arch and output_config.terminal_mode:
            cout("")
            cout(f"{entry.fpga_arch.upper()}", style="magenta")
        last_arch = entry.fpga_arch

        # -- Construct the fpga fields.
        parts = []
        parts.append(cstyle(f"{entry.name:<{name_len}}", style="cyan"))
        if verbose:
            parts.append(f"{entry.fpga_arch:<{fpga_arch_len}}")
            parts.append(f"{entry.fpga_part_num:<{fpga_part_num_len}}")
            parts.append(f"{entry.fpga_size:<{fpga_size_len}}")
        parts.append(f"{entry.description}")

        # -- Print the fpga line.
        cout("".join(parts))

    # -- Show summary.
    if output_config.terminal_mode:
        cout(f"Total of {util.plurality(entries, 'example')}")
        if not verbose:
            cout(
                "Run 'apio examples -v' for additional columns.",
                style="yellow",
            )


@click.command(
    name="list",
    short_help="List the available apio examples.",
    help=APIO_EXAMPLES_LIST_HELP,
)
@options.verbose_option
def _list_cli(verbose: bool):
    """Implements the 'apio examples list' command group."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # --List all available examples.
    list_examples(apio_ctx, verbose)


# ---- apio examples fetch


APIO_EXAMPLES_FETCH_HELP = """
The command ‘apio examples fetch’ fetches the files of the specified example
to the current directory or to the directory specified by the –dst option.
The destination directory does not need to exist, but if it does, it must be
empty.

\b
Examples:
  apio examples fetch alhambra-ii/ledon
  apio examples fetch alhambra-ii/ledon -d foo/bar

[Hint] For the list of available examples, type ‘apio examples list’.
"""


@click.command(
    name="fetch",
    short_help="Fetch the files of an example.",
    help=APIO_EXAMPLES_FETCH_HELP,
)
@click.argument("example", metavar="EXAMPLE", nargs=1, required=True)
@options.dst_option_gen(help="Set a different destination directory.")
def _fetch_cli(
    # Arguments
    example: str,
    # Options
    dst: Path,
):
    """Implements the 'apio examples fetch' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Create the examples manager.
    examples = Examples(apio_ctx)

    dst_dir_path = util.resolve_project_dir(dst)

    # -- Fetch example files.
    examples.copy_example_files(example, dst_dir_path)


# ---- apio examples fetch-board


APIO_EXAMPLES_FETCH_BOARD_HELP = """
The command ‘apio examples fetch-board’ is used to fetch all the Apio examples
for a specific board. The examples are copied to the current directory or to
the specified destination directory if the –dst option is provided.

\b
Examples:
  apio examples fetch-board alhambra-ii             # Fetch to local directory
  apio examples fetch-board alhambra-ii -d foo/bar  # Fetch to foo/bar

[Hint] For the list of available examples, type ‘apio examples list’.
"""


@click.command(
    name="fetch-board",
    short_help="Fetch all examples of a board.",
    help=APIO_EXAMPLES_FETCH_BOARD_HELP,
)
@click.argument("board", metavar="BOARD", nargs=1, required=True)
@options.dst_option_gen(help="Set a different destination directory.")
def _fetch_board_cli(
    # Arguments
    board: str,
    # Options
    dst: Path,
):
    """Implements the 'apio examples fetch-board' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- This fails with an error message if there is no such board.
    apio_ctx.lookup_board_name(board)

    # -- Create the examples manager.
    examples = Examples(apio_ctx)

    dst_dir_path = util.resolve_project_dir(dst)

    # # -- Option: Copy the directory
    examples.copy_board_examples(board, dst_dir_path)


# ---- apio examples

APIO_EXAMPLES_HELP = """
The command group ‘apio examples’ provides subcommands for listing and
fetching Apio-provided examples. Each example is a self-contained mini-project
that can be built and uploaded to an FPGA board.
"""


# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _list_cli,
            _fetch_cli,
            _fetch_board_cli,
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
