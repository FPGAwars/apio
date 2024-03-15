"""Manage apio examples"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo, Juan González
# -- Licence GPLv2

import shutil
from pathlib import Path
import click

from apio import util
from apio.profile import Profile
from apio.resources import Resources

# -- Error messages
EXAMPLE_NOT_FOUND_MSG = """
Warning: this example does not exist
Use `apio examples -l` for listing all the available examples"""

EXAMPLE_OF_USE_CAD = """
Example of use:
   apio examples -f leds
Copy the leds example files to the current directory\n"""

EXAMPLE_DIR_FILE = """
To get an example, use the command:
   apio examples -d/-f name"""


class Examples:
    """Manage the apio examples"""

    def __init__(self):

        # -- Access to the profile information
        profile = Profile()

        # -- Access to the resources
        resources = Resources()

        # -- Apio examples package name
        self.name = "examples"

        # -- Folder where the example packages was installed
        self.examples_dir = util.get_package_dir(self.name)

        # -- Get the example package version
        self.version = util.get_package_version(self.name, profile)

        # -- Get the version restrictions
        self.spec_version = util.get_package_spec_version(self.name, resources)

    def list_examples(self):
        """Print all the examples available"""

        # -- Check if the example package is installed
        installed = util.check_package(
            self.name, self.version, self.spec_version, self.examples_dir
        )

        # -- No package installed: return
        if not installed:
            return 1

        # -- Calculate the terminal width
        terminal_width, _ = shutil.get_terminal_size()

        # -- String with a horizontal line with the same width
        # -- as the terminal
        line = "─" * terminal_width

        # -- Print the header
        click.echo()
        click.echo(line)

        # -- Collect all the board (every folder in the examples packages
        # -- correspond to a board)
        boards = []

        for board in sorted(self.examples_dir.iterdir()):
            if board.is_dir():
                boards.append(board)

        # -- Collect the examples for each board
        # -- Valid examples are folders...
        examples = []
        examples_names = []

        # -- Every board...
        for board in boards:

            # -- Has one or more examples...
            for example in board.iterdir():

                # -- The examples are folders...
                if example.is_dir():

                    # -- Store the example name
                    example_str = f"{board.name}/{example.name}"
                    examples_names.append(example_str)

                    # -- Store the example path
                    examples.append(example)

        # -- For each example, collect the information in the info file
        # -- It contains the example description
        for example, name in zip(examples, examples_names):

            # -- info file
            info = example / "info"

            # -- Not all the folder has info...
            if info.exists():

                # -- Open info file
                with open(info, "r", encoding="utf-8") as info_file:

                    # -- Read info file and remove the new line characters
                    info_data = info_file.read().replace("\n", "")

                    # -- Print the example name and description!
                    click.secho(f"{name}", fg="blue", bold=True)
                    click.secho(f"{info_data}")
                    click.secho(line)

        # -- Print the total examples
        click.secho(f"Total: {len(examples)}")

        # -- Print more info about the examples
        click.secho(EXAMPLE_DIR_FILE, fg="green")
        click.secho(EXAMPLE_OF_USE_CAD, fg="green")
        click.secho()
        return 0

    def copy_example_dir(self, example: str, project_dir: Path, sayno: bool):
        """Copy the example creating the folder
        Ex. The example Alhambra-II/ledon --> the folder Alhambra-II/ledon
        is created
          * INPUTS:
            * example: Example name (Ex. 'Alhambra-II/ledon')
            * project_dir: (optional)
            * sayno: Automatically answer no
        """

        # -- Check if the example package is installed
        installed = util.check_package(
            self.name, self.version, self.spec_version, self.examples_dir
        )

        # -- No package installed: return
        if not installed:
            return 1

        # -- Get the working dir (current or given)
        project_dir = util.check_dir(project_dir)

        # -- Build the destination example path
        dst_example_path = project_dir / example

        # -- Build the source example path (where the example was installed)
        src_example_path = self.examples_dir / example

        # -- If the source example path is not a folder... it is an error
        if not src_example_path.is_dir():
            click.secho(EXAMPLE_NOT_FOUND_MSG, fg="yellow")
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
            * example: Example name (Ex. 'Alhambra-II/ledon')
            * project_dir: (optional)
            * sayno: Automatically answer no
        """

        # -- Check if the example package is installed
        installed = util.check_package(
            self.name, self.version, self.spec_version, self.examples_dir
        )

        # -- No package installed: return
        if not installed:
            return 1

        # -- Get the working dir (current or given)
        dst_example_path = util.check_dir(project_dir)

        # -- Build the source example path (where the example was installed)
        src_example_path = self.examples_dir / example

        # -- If the source example path is not a folder... it is an error
        if not src_example_path.is_dir():
            click.secho(EXAMPLE_NOT_FOUND_MSG, fg="yellow")
            return 1

        # -- Copy the example files!!
        # -- TODO: fix an error...
        exit_code = self._copy_files(
            example, src_example_path, dst_example_path, sayno
        )

        return exit_code

    @staticmethod
    def _copy_files(
        example: str, src_path: Path, dest_path: Path, sayno: bool
    ):
        """Copy the example files to the destination folder
        * INPUTS:
          * example: Name of the example (Ex. 'Alhambra-II/ledon')
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

    @staticmethod
    def _copy_dir(example: str, src_path: Path, dest_path: Path):
        """Copy example of the src_path on the dest_path
        * INPUT
          * example: Name of the example (Ex. 'Alhambra-II/ledon')
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

    @staticmethod
    def examples_of_use_cad():
        """Return the example of use help string"""

        return EXAMPLE_OF_USE_CAD
