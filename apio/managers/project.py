# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Utilities for accesing the apio.ini projects"""

import sys
from os.path import isfile
from pathlib import Path
from configparser import ConfigParser
from typing import Optional
from configobj import ConfigObj
import click
from apio import util
from apio.resources import Resources

# -- Apio projecto filename
PROJECT_FILENAME = "apio.ini"

DEFAULT_TOP_MODULE = "main"

TOP_COMMENT = """\
APIO project configuration file. For details see
https://github.com/FPGAwars/apio/wiki/Project-configuration-file
"""


class Project:
    """Class for managing apio projects"""

    def __init__(self, project_dir: Path):
        # pylint: disable=fixme
        # TODO: Make these __private and provide getter methods.
        self.project_dir = util.get_project_dir(project_dir)
        self.board: str = None
        self.top_module: str = None
        self.native_exe_mode: bool = None

    def create_sconstruct_deprecated(self, arch=None, sayyes=False):
        """Creates a default SConstruct file"""

        sconstruct_name = "SConstruct"
        sconstruct_path = self.project_dir / sconstruct_name
        local_sconstruct_path = (
            util.get_path_in_apio_package("resources") / arch / sconstruct_name
        )

        if sconstruct_path.exists():
            # -- If sayyes, skip the question
            if sayyes:
                self._copy_sconstruct_file_deprecated(
                    sconstruct_name,
                    sconstruct_path,
                    local_sconstruct_path,
                )
            else:
                click.secho(
                    f"Warning: {sconstruct_name} file already exists",
                    fg="yellow",
                )

                if click.confirm("Do you want to replace it?"):
                    self._copy_sconstruct_file_deprecated(
                        sconstruct_name,
                        sconstruct_path,
                        local_sconstruct_path,
                    )
                else:
                    click.secho("Abort!", fg="red")

        else:
            self._copy_sconstruct_file_deprecated(
                sconstruct_name, sconstruct_path, local_sconstruct_path
            )

    def create_ini_deprecated(self, board, top_module, sayyes=False):
        """Creates a new apio project file"""

        # -- Build the filename
        ini_path = self.project_dir / PROJECT_FILENAME

        # Check board
        boards = Resources().boards
        if board not in boards.keys():
            click.secho(f"Error: no such board '{board}'", fg="red")
            sys.exit(1)

        # -- The apio.ini file already exists...
        if ini_path.is_file():

            # -- Warn the user, unless the flag sayyes is active
            if not sayyes:
                click.secho(
                    f"Warning: {PROJECT_FILENAME} file already exists",
                    fg="yellow",
                )

                # -- Ask for confirmation
                replace = click.confirm("Do you want to replace it?")

                # -- User say: NO! --> Abort
                if not replace:
                    click.secho("Abort!", fg="red")
                    return

        # -- Create the apio.ini from scratch
        self._create_ini_file_deprecated(
            board, top_module, ini_path, PROJECT_FILENAME
        )

    @staticmethod
    def create_ini(project_dir, board, top_module, sayyes=False) -> bool:
        """Creates a new apio project file. Returns True if ok."""

        # -- Construct the path
        ini_path = project_dir / PROJECT_FILENAME

        # -- Verify that the board id is valid.
        boards = Resources().boards
        if board not in boards.keys():
            click.secho(f"Error: no such board '{board}'", fg="red")
            return False

        # -- If the ini file already exists, ask if it's ok to delete.
        if ini_path.is_file():

            # -- Warn the user, unless the flag sayyes is active
            if not sayyes:
                click.secho(
                    f"Warning: {PROJECT_FILENAME} file already exists",
                    fg="yellow",
                )

                # -- Ask for confirmation
                replace = click.confirm("Do you want to replace it?")

                # -- User say: NO! --> Abort
                if not replace:
                    click.secho("Abort!", fg="red")
                    return False

        # -- Create the apio.ini from scratch.
        click.secho(f"Creating {ini_path} file ...")
        config = ConfigObj(str(ini_path))
        config.initial_comment = TOP_COMMENT.split("\n")
        config["env"] = {}
        config["env"]["board"] = board
        config["env"]["top-module"] = top_module
        config.write()
        click.secho(
            f"The file '{ini_path}' was created successfully.\n"
            "Run the apio clean command for project consistency.",
            fg="green",
        )
        return True

    def update_ini_deprecated(self, top_module):
        """Update the current init file with the given top-module"""

        # -- Build the filename
        ini_path = self.project_dir / PROJECT_FILENAME

        # -- Check if the apio.ini file exists
        if not ini_path.is_file():
            click.secho(
                "No apio.ini file. You should first create it:\n"
                "  apio init --board <boardname>\n",
                fg="red",
            )
            return

        # -- Read the current apio.ini file
        config = ConfigParser()
        config.read(ini_path)

        # -- Set the new top-mddule
        self.top_module = top_module
        config.set("env", "top-module", top_module)

        # -- Write the apio ini file
        with open(ini_path, "w", encoding="utf-8") as inifile:
            config.write(inifile)

        click.secho(
            f"File '{PROJECT_FILENAME}' has been successfully updated!",
            fg="green",
        )

    @staticmethod
    def modify_ini_file(
        project_dir: Path, board: Optional[str], top_module: Optional[str]
    ) -> bool:
        """Update the current ini file with the given optional parameters.
        Returns True if ok."""

        # -- construct the file path.
        ini_path = project_dir / PROJECT_FILENAME

        # -- Verify that the board id is valid.
        if board:
            boards = Resources().boards
            if board not in boards.keys():
                click.secho(
                    f"Error: no such board '{board}'.\n"
                    "Use 'apio boards -l' to list supported boards.",
                    fg="red",
                )
                return False

        # -- Check if the apio.ini file exists
        if not ini_path.is_file():
            click.secho(
                f"Error: '{ini_path}' not found. You should create it first.\n"
                "see 'apio create -h' for more details.",
                fg="red",
            )
            return False

        # -- Read the current apio.ini file
        config = ConfigObj(str(ini_path))

        # -- Set specified fields.
        if board:
            config["env"]["board"] = board

        if top_module:
            config["env"]["top-module"] = top_module

        # -- Write the apio ini file
        config.write()

        click.secho(
            f"File '{ini_path}' was modified successfully.\n"
            f"Run the apio clean command for project consistency.",
            fg="green",
        )
        return True

    @staticmethod
    def _create_ini_file_deprecated(board, top_module, ini_path, ini_name):
        click.secho(f"Creating {ini_name} file ...")
        with open(ini_path, "w", encoding="utf8") as file:
            config = ConfigParser()
            config.add_section("env")

            # Set the required attributes.
            config.set("env", "board", board)
            config.set("env", "top-module", top_module)

            # -- Write the apio ini file
            config.write(file)
            click.secho(
                f"File '{ini_name}' has been successfully created!",
                fg="green",
            )

    @staticmethod
    def _copy_sconstruct_file_deprecated(
        sconstruct_name, sconstruct_path, local_sconstruct_path
    ):
        click.secho(f"Creating {sconstruct_name} file ...")

        # -- Define the target sconstruct file to create
        with sconstruct_path.open(mode="w", encoding="utf8") as sconstruct:
            # -- Open the original sconstruct file
            with local_sconstruct_path.open(
                encoding="utf8"
            ) as local_sconstruct:
                # -- Copy the src to the target file
                sconstruct.write(local_sconstruct.read())

                click.secho(
                    f"File '{sconstruct_name}' has been successfully created!",
                    fg="green",
                )

    def read(self):
        """Read the project config file"""

        project_file = self.project_dir / PROJECT_FILENAME

        # -- If no project file found, just return
        if not isfile(project_file):
            click.secho(
                f"Info: Project has no {PROJECT_FILENAME} file", fg="yellow"
            )
            return

        # pylint: disable=fixme
        # TODO: Can we replace ConfigParser with ConfigObj for consistency?

        # Load the project file.
        config_parser = ConfigParser()
        config_parser.read(project_file)

        for section in config_parser.sections():
            if section != "env":
                click.secho(
                    f"Project file {project_file} has an invalid "
                    "section named "
                    f"[{section}].",
                    fg="red",
                )
                sys.exit(1)

        if "env" not in config_parser.sections():
            click.secho(
                f"Project file {project_file} does not have an "
                "[env] section.",
                fg="red",
            )
            sys.exit(1)

        # Parse attributes in the env section.
        parsed_attributes = set()
        self.board = self._parse_board(config_parser, parsed_attributes)
        self.top_module = self._parse_top_module(
            config_parser, parsed_attributes
        )
        exe_mode = self._parse_exe_mode(config_parser, parsed_attributes)
        self.native_exe_mode = {"default": False, "native": True}[exe_mode]

        # Verify that the project file (api.ini) doesn't contain additional
        # (illegal) keys that where not parsed
        for attribute in config_parser.options("env"):
            if attribute not in parsed_attributes:
                click.secho(
                    f"Project file {project_file} contains"
                    f" an unknown attribute '{attribute}'.",
                    fg="red",
                )
                sys.exit(1)

    @staticmethod
    def _parse_board(
        config_parser: ConfigParser, parsed_attributes: set[str]
    ) -> str:
        """Parse the configured board from the project
            file parser and add the keys used
          to parsed_attributes.
        RETURN:
          * A string with the name of the board
        """
        parsed_attributes.add("board")
        board = config_parser.get("env", "board", fallback=None)
        if not board:
            click.secho(
                "Error: Missing required 'board' specification "
                f"in {PROJECT_FILENAME}",
                fg="red",
            )
            sys.exit(1)
        return board

    @staticmethod
    def _parse_top_module(
        config_parser: ConfigParser, parsed_attributes: set[str]
    ) -> str:
        """Read the configured top-module from the project file
        parser and add the keys used
          to parsed_attributes.
        RETURN:
          * A string with the name of the top-module
        """
        parsed_attributes.add("top-module")
        top_module = config_parser.get("env", "top-module", fallback=None)
        if not top_module:
            click.secho(
                f"Warning: Missing 'top-module' specification in "
                f"{PROJECT_FILENAME}, assuming 'main'",
                fg="yellow",
            )
            click.secho("No 'top-module' in [env] section. Assuming 'main'.")
            return DEFAULT_TOP_MODULE
        return top_module

    @staticmethod
    def _parse_exe_mode(
        config_parser: ConfigParser, parsed_attributes: set[str]
    ) -> str:
        """Read the configured exe mode from the
            project file parser and add the keys used
          to parsed_attributes.
        RETURN:
          * A string with "default" (default) or "native"
        """
        parsed_attributes.add("exe-mode")
        exe_mode = config_parser.get("env", "exe-mode", fallback="default")
        if exe_mode not in {"default", "native"}:
            click.secho(
                f"Error: invalid {PROJECT_FILENAME} project file\n"
                "Optional attribute 'exe-mode' should have"
                " the value 'default' or 'native'.",
                fg="red",
            )
            sys.exit(1)
        return exe_mode
