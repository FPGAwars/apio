# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Utilities for accesing the apio.ini projects"""

# TODO(zapta): Deprecate the mutations of existing api.ini file.

# TODO(zapta): Deprecate the copying of the sconstruct file.
# This is a developer only feature and developers can copy
# it manually as needed.

import sys
from os.path import isfile
from pathlib import Path

# -- Config Parser: Use INI config files with easy
# https://docs.python.org/3/library/configparser.html
from configparser import ConfigParser
import click
from apio import util
from apio.resources import Resources

# -- Apio projecto filename
PROJECT_FILENAME = "apio.ini"


class Project:
    """Class for managing apio projects"""

    def __init__(self):
        # TODO(zapta): Make these __private and provide getter methods.
        self.board = None
        self.top_module = None
        self.exe_mode = None

    def create_sconstruct(self, project_dir: Path, arch=None, sayyes=False):
        """Creates a default SConstruct file"""

        project_dir = util.check_dir(project_dir)

        sconstruct_name = "SConstruct"
        sconstruct_path = project_dir / sconstruct_name
        local_sconstruct_path = (
            util.get_full_path("resources") / arch / sconstruct_name
        )

        if sconstruct_path.exists():
            # -- If sayyes, skip the question
            if sayyes:
                self._copy_sconstruct_file(
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
                    self._copy_sconstruct_file(
                        sconstruct_name,
                        sconstruct_path,
                        local_sconstruct_path,
                    )
                else:
                    click.secho("Abort!", fg="red")

        else:
            self._copy_sconstruct_file(
                sconstruct_name, sconstruct_path, local_sconstruct_path
            )

    def create_ini(self, board, top_module, project_dir="", sayyes=False):
        """Creates a new apio project file"""

        project_dir = util.check_dir(project_dir)

        # -- Build the filename
        ini_path = project_dir / PROJECT_FILENAME

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
        self._create_ini_file(board, top_module, ini_path, PROJECT_FILENAME)

    # TODO- Deprecate prgramatic mutations of apio.ini
    def update_ini(self, top_module, project_dir):
        """Update the current init file with the given top-module"""

        project_dir = util.check_dir(project_dir)

        # -- Build the filename
        ini_path = project_dir / PROJECT_FILENAME

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
    def _create_ini_file(board, top_module, ini_path, ini_name):
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
    def _copy_sconstruct_file(
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

        # -- If no project finel found, just return
        if not isfile(PROJECT_FILENAME):
            print(f"Info: No {PROJECT_FILENAME} file")
            return

        # Load the project file.
        config_parser = ConfigParser()
        config_parser.read(PROJECT_FILENAME)

        for section in config_parser.sections():
            if section != "env":
                message = (
                    f"Project file {PROJECT_FILENAME} "
                    f"has an invalid section named "
                    f"[{section}]."
                )
                print(message)
                sys.exit(1)

        if "env" not in config_parser.sections():
            message = (
                f"Project file {PROJECT_FILENAME}"
                f"does not have an [env] section."
            )
            print(message)
            sys.exit(1)

        # Parse attributes in the env section.
        parsed_attributes = set()
        self.board = self._parse_board(config_parser, parsed_attributes)
        self.top_module = self._parse_top_module(
            config_parser, parsed_attributes
        )
        self.exe_mode = self._parse_exe_mode(config_parser, parsed_attributes)

        # Verify that the project file (api.ini) doesn't contain additional
        # (illegal) keys that where not parsed
        for attribute in config_parser.options("env"):
            if attribute not in parsed_attributes:
                message = (
                    f"Project file {PROJECT_FILENAME} contains"
                    f" an unknown attribute '{attribute}'."
                )
                print(message)
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
        board = config_parser.get("env", "board")
        if not board:
            print(f"Error: invalid {PROJECT_FILENAME} project file")
            print("No 'board' field defined in [env] section")
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
        top_module = config_parser.get("env", "top-module")
        if not top_module:
            click.secho(
                f"Warning! invalid {PROJECT_FILENAME} " f"project file",
                fg="yellow",
            )
            click.secho("No 'top-module' in [env] section. Assuming 'main'.")
            return "main"
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
        # print(f"*** project.py:  reading exe mode")
        parsed_attributes.add("exe-mode")
        exe_mode = config_parser.get("env", "exe-mode", fallback="default")
        if exe_mode not in {"default", "native"}:
            print(f"Error: invalid {PROJECT_FILENAME}" "project file")
            print(
                "Optional attribute 'exe-mode' should have"
                " the value 'default' or 'native'."
            )
            sys.exit(1)
        return exe_mode
