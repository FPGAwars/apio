"""Manage apio examples"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo, Juan González
# -- License GPLv2

import shutil
import sys
import os
from pathlib import Path, PosixPath
from dataclasses import dataclass
from typing import Optional, List, Dict
from apio.common.apio_console import cout, cstyle, cerror
from apio.apio_context import ApioContext
from apio.managers import installer


@dataclass
class ExampleInfo:
    """Information about a single example."""

    board_dir_name: str
    example_dir_name: str
    path: PosixPath
    description: str
    fpga_arch: str
    fpga_part_num: str
    fpga_size: str

    @property
    def name(self) -> str:
        """Returns the full id of the example."""
        return self.board_dir_name + "/" + self.example_dir_name


class Examples:
    """Manage the apio examples"""

    def __init__(self, apio_ctx: ApioContext):

        # -- Save the apio context.
        self.apio_ctx = apio_ctx

        # -- Folder where the example packages was installed
        self.examples_dir = apio_ctx.get_package_dir("examples")

    def is_dir_empty(self, path: Path) -> bool:
        """Return true if the given dir is empty, ignoring hidden entry.
        That is, the dir may contain only hidden entries.
        We use this relaxed criteria of emptiness to avoid user confusion.
        We could use glop.glob() but in python 3.10 and earlier it doesn't
        have the 'include_hidden' argument.
        """
        # -- Check prerequisites.
        assert path.is_dir(), f"Not a dir: {path}"

        # -- Iterate directory entries
        for name in os.listdir(path):
            # -- If not a hidden entry, answer is no.
            if not name.startswith("."):
                return False
        # -- Non hidden entries not found. Directory is empty.
        return True

    def get_examples_infos(self) -> List[ExampleInfo]:
        """Scans the examples and returns a list of ExampleInfos.
        Returns null if an error."""

        # -- Check that the example package is installed
        installer.install_missing_packages_on_the_fly(self.apio_ctx)

        # -- Collect the examples home dir each board.
        boards_dirs: List[PosixPath] = []

        for board_dir in self.examples_dir.iterdir():
            if board_dir.is_dir():
                boards_dirs.append(board_dir)

        # -- Collect the examples of each boards.
        examples: List[ExampleInfo] = []
        for board_dir in boards_dirs:

            # -- Iterate board's example subdirectories.
            for example_dir in board_dir.iterdir():

                # -- Skip files. We care just about directories.
                if not example_dir.is_dir():
                    continue

                # -- Try to load description from the example info file.
                info_file = example_dir / "info"
                if info_file.exists():
                    with open(info_file, "r", encoding="utf-8") as f:
                        description = f.read().replace("\n", "")
                else:
                    description = ""

                # -- Extract the fpga arch and part number, with "" as
                # -- default value if not found.
                board_info = self.apio_ctx.boards.get(board_dir.name, {})
                fpga_id = board_info.get("fpga", "")
                fpga_info = self.apio_ctx.fpgas.get(fpga_id, {})
                fpga_arch = fpga_info.get("arch", "")
                fpga_part_num = fpga_info.get("part_num", "")
                fpga_size = fpga_info.get("size", "")

                # -- Append this example to the list.
                example_info = ExampleInfo(
                    board_dir_name=board_dir.name,
                    example_dir_name=example_dir.name,
                    path=example_dir,
                    description=description,
                    fpga_arch=fpga_arch,
                    fpga_part_num=fpga_part_num,
                    fpga_size=fpga_size,
                )
                examples.append(example_info)

        # -- Sort in-place by acceding example name, case insensitive.
        examples.sort(key=lambda x: x.name.lower())

        return examples

    def count_examples_by_board(self) -> Dict[str, int]:
        """Returns a dictionary with example count per board. Boards
        that have no examples are not included in the dictionary."""

        # -- Make sure that the examples package is installed.
        installer.install_missing_packages_on_the_fly(self.apio_ctx)

        # -- Get list of examples.
        examples: List[ExampleInfo] = self.get_examples_infos()

        # -- Count examples by board
        counts: Dict[str, int] = {}
        for example in examples:
            board = example.board_dir_name
            old_count = counts.get(board, 0)
            counts[board] = old_count + 1

        # -- All done
        return counts

    def lookup_example_info(self, example_name) -> Optional[ExampleInfo]:
        """Return the example info for given example or None if not found.
        Example_name looks like 'alhambra-ii/ledon'.
        """

        example_infos = self.get_examples_infos()
        for ex in example_infos:
            if example_name == ex.name:
                return ex
        return None

    def copy_example_files(self, example_name: str, dst_dir_path: Path):
        """Copy the files from the given example to the destination dir.
        If destination dir exists, it must be empty.
        If it doesn't exist, it's created with any necessary parent.
        The arg 'example_name' looks like 'alhambra-ii/ledon'.
        """

        # -- Check that the examples package is installed.
        installer.install_missing_packages_on_the_fly(self.apio_ctx)

        # Check that the example name exists.
        example_info: ExampleInfo = self.lookup_example_info(example_name)

        if not example_info:
            cerror(f"Example '{example_name}' not found.")
            cout(
                "Run 'apio example list' for the list of examples.",
                "Expecting an example name like alhambra-ii/ledon.",
                style="yellow",
            )
            sys.exit(1)

        # -- Get the example dir path.
        src_example_path = example_info.path

        # -- Prepare an empty destination directory. To avoid confusion,
        # -- we ignore hidden files and directory.
        if dst_dir_path.is_dir():
            if not self.is_dir_empty(dst_dir_path):
                cerror(
                    f"Destination directory '{str(dst_dir_path)}' "
                    "is not empty."
                )
                sys.exit(1)
        else:
            dst_dir_path.mkdir(parents=True, exist_ok=False)

        cout("Copying " + example_name + " example files.")

        # -- Go though all the files in the example folder.
        for file in src_example_path.iterdir():
            # -- Copy the file unless it's 'info' which we ignore.
            if file.name != "info":
                shutil.copy(file, dst_dir_path)
                styled_name = cstyle(os.path.basename(file), style="cyan")
                cout(f"Fetched file {styled_name}")

        # -- Inform the user.
        cout("Example fetched successfully.", style="green")

    def get_board_examples(self, board_name) -> List[ExampleInfo]:
        """Returns the list of examples with given board name."""
        return [
            x
            for x in self.get_examples_infos()
            if x.board_dir_name == board_name
        ]

    def copy_board_examples(self, board_name: str, dst_dir: Path):
        """Copy the example creating the folder
        Ex. The example alhambra-ii/ledon --> the folder alhambra-ii/ledon
        is created
          * INPUTS:
            * example: Example name (Ex. 'alhambra-ii/ledon')
            * project_dir: (optional)
            * sayno: Automatically answer no
        """

        # -- Check that the examples package is installed.
        installer.install_missing_packages_on_the_fly(self.apio_ctx)

        # -- Get the working dir (current or given)
        # dst_dir = util.resolve_project_dir(
        #     dst_dir, create_if_missing=True
        # )
        board_examples = self.get_board_examples(board_name)
        if not board_examples:
            cerror(f"No examples for board '{board_name}.")
            cout(
                "Run 'apio examples list' for the list of examples.",
                "Expecting a board name such as 'alhambra-ii.",
                style="yellow",
            )
            sys.exit(1)

        # -- Build the destination example path
        dst_board_dir = dst_dir / board_name

        # -- Build the source example path (where the example was installed)
        src_board_dir = self.examples_dir / board_name

        # -- If the source example path is not a folder... it is an error
        if not src_board_dir.is_dir():
            cerror(f"Examples for board [{board_name}] not found.")
            cout(
                "Run 'apio examples list' for the list of available "
                "examples.",
                "Expecting a board name such as 'alhambra-ii'.",
                style="yellow",
            )
            sys.exit(1)

        if dst_board_dir.is_dir():
            # -- To avoid confusion to the user, we ignore hidden files.
            if not self.is_dir_empty(dst_board_dir):
                cerror(
                    f"Destination directory '{str(dst_board_dir)}' "
                    "is not empty."
                )
                sys.exit(1)
        else:
            cout(f"Creating directory {dst_board_dir}.")
            dst_board_dir.mkdir(parents=True, exist_ok=False)

        # -- Copy the directory tree.
        shutil.copytree(src_board_dir, dst_board_dir, dirs_exist_ok=True)

        for example_name in os.listdir(dst_board_dir):
            styled_name = cstyle(f"{board_name}/{example_name}", style="cyan")
            cout(f"Fetched example {styled_name}")

        cout("Board examples fetched successfully.", style="green")
