"""Manage apio examples"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo, Juan González
# -- Licence GPLv2

import shutil
from pathlib import Path, PosixPath
from dataclasses import dataclass
from typing import Optional, List
import click
from apio import util
from apio import pkg_util
from apio.apio_context import ApioContext


@dataclass
class ExampleInfo:
    """Information about a single example."""

    name: str
    path: PosixPath
    description: str


class Examples:
    """Manage the apio examples"""

    def __init__(self, apio_ctx: ApioContext):

        # -- Save the apio context.
        self.apio_ctx = apio_ctx

        # -- Folder where the example packages was installed
        self.examples_dir = apio_ctx.get_package_dir("examples") / "examples"

    def get_examples_infos(self) -> Optional[List[ExampleInfo]]:
        """Scans the examples and returns a list of ExampleInfos.
        Returns null if an error."""

        # -- Check that the example package is installed
        pkg_util.check_required_packages(self.apio_ctx, ["examples"])

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

                # -- Append this example to the list.
                name = f"{board_dir.name}/{example_dir.name}"
                example_info = ExampleInfo(name, example_dir, description)
                examples.append(example_info)

        # -- Sort in-place by ascceding example name, case insensitive.
        examples.sort(key=lambda x: x.name.lower())

        return examples

    def list_examples(self) -> None:
        """Print all the examples available. Return a process exit
        code, 0 if ok, non zero otherwise."""

        # -- Check that the examples package is installed.
        pkg_util.check_required_packages(self.apio_ctx, ["examples"])

        # -- Get list of examples.
        examples: List[ExampleInfo] = self.get_examples_infos()
        if examples is None:
            # -- Error message is aleady printed.
            return 1

        # -- Get terminal configuration. We format the report differently for
        # -- a terminal and for a pipe.
        output_config = util.get_terminal_config()

        # -- For terminal, print a header with an horizontal line across the
        # -- terminal.
        if output_config.terminal_mode():
            terminal_seperator_line = "─" * output_config.terminal_width
            click.secho()
            click.secho(terminal_seperator_line)

        # -- For a pipe, determine the max example name length.
        max_example_name_len = max(len(x.name) for x in examples)

        # -- Emit the examples
        for example in examples:
            if output_config.terminal_mode():
                # -- For a terminal. Multi lines and colors.
                click.secho(f"{example.name}", fg="blue", bold=True)
                click.secho(f"{example.description}")
                click.secho(terminal_seperator_line)
            else:
                # -- For a pipe, single line, no colors.
                click.secho(
                    f"{example.name:<{max_example_name_len}}  |  "
                    f"{example.description}"
                )

        # -- For a terminal, emit additional summary.
        if output_config.terminal_mode():
            click.secho(f"Total: {len(examples)}")

        return 0

    def copy_example_dir(self, example: str, project_dir: Path, sayno: bool):
        """Copy the example creating the folder
        Ex. The example alhambra-ii/ledon --> the folder alhambra-ii/ledon
        is created
          * INPUTS:
            * example: Example name (Ex. 'alhambra-ii/ledon')
            * project_dir: (optional)
            * sayno: Automatically answer no
        """

        # -- Check that the examples package is installed.
        pkg_util.check_required_packages(self.apio_ctx, ["examples"])

        # -- Get the working dir (current or given)
        project_dir = util.get_project_dir(project_dir, create_if_missing=True)

        # -- Build the destination example path
        dst_example_path = project_dir / example

        # -- Build the source example path (where the example was installed)
        src_example_path = self.examples_dir / example

        # -- If the source example path is not a folder... it is an error
        if not src_example_path.is_dir():
            click.secho(f"Error: example [{example}] not found.", fg="red")
            return 1

        # -- The destination path is a folder...It means that the
        # -- example already exist! Ask the user that to do...
        # -- Replace it or not...
        if dst_example_path.is_dir():

            # -- If sayno, do not copy anything
            if not sayno:

                # -- Warn the user
                click.secho(
                    "Warning: " + example + " directory already exists",
                    fg="yellow",
                )

                # -- Ask the user what to do...
                if click.confirm("Do you want to replace it?"):

                    # -- Remove the old example
                    shutil.rmtree(dst_example_path)

                    # -- Copy the example!
                    self._copy_dir(example, src_example_path, dst_example_path)

        elif dst_example_path.is_dir():
            click.secho(
                "Warning: " + example + " is already a file",
                fg="yellow",
            )
        else:
            self._copy_dir(example, src_example_path, dst_example_path)

        return 0

    def copy_example_files(self, example: str, project_dir: Path, sayno: bool):
        """Copy the example files (not the initial folders)
        * INPUTS:
            * example: Example name (Ex. 'alhambra-ii/ledon')
            * project_dir: (optional)
            * sayno: Automatically answer no
        """

        # -- Check that the examples package is installed.
        pkg_util.check_required_packages(self.apio_ctx, ["examples"])

        # -- Get the working dir (current or given)
        dst_example_path = util.get_project_dir(
            project_dir, create_if_missing=True
        )

        # -- Build the source example path (where the example was installed)
        src_example_path = self.examples_dir / example

        # -- If the source example path is not a folder. it is an error
        if not src_example_path.is_dir():
            click.secho(f"Error: example [{example}] not found.", fg="red")
            return 1

        # -- Copy the example files!!
        # -- TODO: fix an error.
        exit_code = self._copy_files(
            example, src_example_path, dst_example_path, sayno
        )

        return exit_code

    def _copy_files(
        self, example: str, src_path: Path, dest_path: Path, sayno: bool
    ):
        """Copy the example files to the destination folder
        * INPUTS:
          * example: Name of the example (Ex. 'alhambra-ii/ledon')
          * src_path: Source folder to copy
          * dest_path: Destination folder
        """

        # -- Inform the user
        click.secho("Copying " + example + " example files ...")

        # -- Go though all the files in the example folder...
        for file in src_path.iterdir():

            # -- Get the filename
            filename = file.name

            # -- "info" file is not copied
            if filename != "info":

                # -- Build the destination filepath
                dst_filename = dest_path / filename

                # -- Check if the destination final exists
                # -- It is is the case, ask the user what to do...
                if dst_filename.is_file():

                    # -- If sayno, do not copy the file. Move to the next
                    if sayno:
                        continue

                    # -- Warn the user
                    click.secho(
                        f"Warning: {filename} file already exists",
                        fg="yellow",
                    )

                    # -- Ask the user
                    if click.confirm("Do you want to replace it?"):

                        # -- copy the file
                        shutil.copy(file, dest_path)

                # -- The destination path is a folder!
                elif dst_filename.is_dir():

                    # -- Warn the user. Nothing is copied...
                    click.secho(
                        f"Warning: {filename} is already a directory",
                        fg="yellow",
                    )
                    return 1

                # -- Copy the file!
                else:
                    shutil.copy(file, dest_path)

        # -- Inform the user!
        click.secho(
            f"Example files '{example}' have been successfully created!",
            fg="green",
        )

        return 0

    def _copy_dir(self, example: str, src_path: Path, dest_path: Path):
        """Copy example of the src_path on the dest_path
        * INPUT
          * example: Name of the example (Ex. 'alhambra-ii/ledon')
          * src_path: Source folder to copy
          * dest_path: Destination folder
        """

        # -- Infor for the user
        click.secho("Creating " + example + " directory ...")

        # -- Copy the src folder on to the destination path
        shutil.copytree(src_path, dest_path)

        # -- Info for the user
        click.secho(
            "Example '" + example + "' has been successfully created!",
            fg="green",
        )
