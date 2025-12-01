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
from apio.common.apio_styles import INFO, SUCCESS, EMPH3
from apio.apio_context import ApioContext
from apio.utils import util


@dataclass
class ExampleInfo:
    """Information about a single example."""

    board_id: str
    example_name: str
    path: PosixPath
    description: str
    fpga_arch: str
    fpga_part_num: str
    fpga_size: str

    @property
    def name(self) -> str:
        """Returns the full id of the example."""
        return self.board_id + "/" + self.example_name


class Examples:
    """Manage the apio examples"""

    def __init__(self, apio_ctx: ApioContext):

        # -- Save the apio context.
        self.apio_ctx = apio_ctx

        # -- Folder where the example packages was installed
        self.examples_dir = apio_ctx.get_package_dir("examples")

    def check_dst_dir_is_empty(self, path: Path):
        """Check that the destination directory at the path is empty. If not,
        print an error and exit.
        """

        # -- Check prerequisites.
        assert path.is_dir(), f"Not a dir: {path}"

        # -- Get the dir content,  including hidden entries.
        dir_content: List[str] = os.listdir(path)

        # -- We don't care about macOS
        ignore_list = [".DS_Store"]
        dir_content = [f for f in dir_content if f not in ignore_list]

        # -- Error if not empty.
        if dir_content:
            cerror(
                f"Destination directory '{str(path)}' "
                f"is not empty (e.g, '{dir_content[0]}')."
            )
            sys.exit(1)

    def get_examples_infos(self) -> List[ExampleInfo]:
        """Scans the examples and returns a list of ExampleInfos.
        Returns null if an error."""

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
                fpga_id = board_info.get("fpga-id", "")
                fpga_info = self.apio_ctx.fpgas.get(fpga_id, {})
                fpga_arch = fpga_info.get("arch", "")
                fpga_part_num = fpga_info.get("part-num", "")
                fpga_size = fpga_info.get("size", "")

                # -- Append this example to the list.
                example_info = ExampleInfo(
                    board_id=board_dir.name,
                    example_name=example_dir.name,
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

        # -- Get list of examples.
        examples: List[ExampleInfo] = self.get_examples_infos()

        # -- Count examples by board
        counts: Dict[str, int] = {}
        for example in examples:
            board = example.board_id
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

        # Check that the example name exists.
        example_info: ExampleInfo = self.lookup_example_info(example_name)

        if not example_info:
            cerror(f"Example '{example_name}' not found.")
            cout(
                "Run 'apio example list' for the list of examples.",
                "Expecting an example name like alhambra-ii/ledon.",
                style=INFO,
            )
            sys.exit(1)

        # -- Get the example dir path.
        src_example_path = example_info.path

        # -- Prepare an empty destination directory. To avoid confusion,
        # -- we ignore hidden files and directory.
        if dst_dir_path.exists():
            self.check_dst_dir_is_empty(dst_dir_path)
        else:
            dst_dir_path.mkdir(parents=True, exist_ok=False)

        cout("Copying " + example_name + " example files.")

        # -- Go though all the files in the example folder.
        for entry_path in src_example_path.iterdir():
            # -- Case 1: Skip 'info' files.
            if entry_path.name == "info":
                continue
            # -- Case 2: Copy subdirectory.
            if entry_path.is_dir():
                shutil.copytree(
                    entry_path,  # src
                    dst_dir_path / entry_path.name,  # dst
                    dirs_exist_ok=False,
                )
                continue
            # -- Case 3: Copy file.
            shutil.copy(entry_path, dst_dir_path)

        # -- Inform the user.
        cout(f"Example '{example_name}' fetched successfully.", style=SUCCESS)

    def get_board_examples(self, board_id) -> List[ExampleInfo]:
        """Returns the list of examples with given board id."""
        return [x for x in self.get_examples_infos() if x.board_id == board_id]

    def copy_board_examples(self, board_id: str, dst_dir: Path):
        """Copy the example creating the folder
        Ex. The example alhambra-ii/ledon --> the folder alhambra-ii/ledon
        is created
          * INPUTS:
            * board_id: e.g. 'alhambra-ii.
            * dst_dir: (optional) destination directory.
        """

        # -- Get the working dir (current or given)
        # dst_dir = util.resolve_project_dir(
        #     dst_dir, create_if_missing=True
        # )
        board_examples: List[ExampleInfo] = self.get_board_examples(board_id)

        if not board_examples:
            cerror(f"No examples for board '{board_id}.")
            cout(
                "Run 'apio examples list' for the list of examples.",
                "Expecting a board id such as 'alhambra-ii.",
                style=INFO,
            )
            sys.exit(1)

        # -- Build the source example path (where the example was installed)
        src_board_dir = self.examples_dir / board_id

        # -- If the source example path is not a folder... it is an error
        if not src_board_dir.is_dir():
            cerror(f"Examples for board [{board_id}] not found.")
            cout(
                "Run 'apio examples list' for the list of available "
                "examples.",
                "Expecting a board id such as 'alhambra-ii'.",
                style=INFO,
            )
            sys.exit(1)

        if dst_dir.exists():
            self.check_dst_dir_is_empty(dst_dir)
        else:
            cout(f"Creating directory {dst_dir}.")
            dst_dir.mkdir(parents=True, exist_ok=False)

        # -- Create an ignore callback to skip 'info' files.
        ignore_callback = shutil.ignore_patterns("info")

        cout(
            f'Found {util.plurality(board_examples, "example")} '
            f"for board '{board_id}'"
        )

        for board_example in board_examples:
            example_name = board_example.example_name
            styled_name = cstyle(example_name, style=EMPH3)
            cout(f"Fetching {board_id}/{styled_name}")
            shutil.copytree(
                src_board_dir / example_name,
                dst_dir / example_name,
                dirs_exist_ok=False,
                ignore=ignore_callback,
            )

        cout(
            f"{util.plurality(board_examples, 'Example', include_num=False)} "
            "fetched successfully.",
            style=SUCCESS,
        )
