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

# -- Config Parser: Use INI config files with easy
# https://docs.python.org/3/library/configparser.html
import configparser
import click
from apio import util
from apio.resources import Resources

# -- Apio projecto filename
PROJECT_FILENAME = "apio.ini"


class Project:
    """Class for managing apio projects"""

    def __init__(self):
        self.board = None

        # -- Top module by default: main
        self.top_module = "main"

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
        config = configparser.ConfigParser()
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
            config = configparser.ConfigParser()
            config.add_section("env")
            config.set("env", "board", board)

            # -- Set the top module
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

        # -- Read stored board
        board = self._read_board()

        # -- Read stored top-module
        top_module = self._read_top_module()

        # -- Update board
        self.board = board
        if not board:
            print("Error: invalid {PROJECT_FILENAME} project file")
            print("No 'board' field defined in project file")
            sys.exit(1)

        # -- Update top-module
        self.top_module = top_module

        # -- Warn the user the top module has not been set in the apio.ini
        # -- file
        if not top_module:
            click.secho("Warning! No TOP-MODULE in apio.ini", fg="yellow")

    @staticmethod
    def _read_board() -> str:
        """Read the configured board from the project file
        RETURN:
          * A string with the name of the board
        """

        config = configparser.ConfigParser()
        config.read(PROJECT_FILENAME)
        board = config.get("env", "board")

        return board

    @staticmethod
    def _read_top_module() -> str:
        """Read the configured top-module from the project file
        RETURN:
          * A string with the name of the top-module
        """

        config = configparser.ConfigParser()
        config.read(PROJECT_FILENAME)

        try:
            top_module = config.get("env", "top-module")
        except configparser.NoOptionError:
            top_module = None

        return top_module
