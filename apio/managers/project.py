# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Juan González, Jesús Arroyo
# -- Licence GPLv2
"""TODO"""

import sys
from os.path import isfile
from pathlib import Path

# -- Config Parser: Use INI config files with easy
# https://docs.python.org/3/library/configparser.html
import configparser

import click


from apio import util
from apio.resources import Resources

PROJECT_FILENAME = "apio.ini"


class Project:
    """TODO"""

    def __init__(self):
        self.board = None

    def create_sconstruct(self, project_dir="", arch=None, sayyes=False):
        """Creates a default SConstruct file"""

        project_dir = Path(util.check_dir(project_dir))

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

    def create_ini(self, board, project_dir="", sayyes=False):
        """Creates a new apio project file"""

        project_dir = util.check_dir(project_dir)

        # -- Build the filename
        ini_path = str(Path(project_dir) / PROJECT_FILENAME)

        # Check board
        boards = Resources().boards
        if board not in boards.keys():
            click.secho(f"Error: no such board '{board}'", fg="red")
            sys.exit(1)

        if isfile(ini_path):
            # -- If sayyes, skip the question
            if sayyes:
                self._create_ini_file(board, ini_path, PROJECT_FILENAME)
            else:
                click.secho(
                    f"Warning: {PROJECT_FILENAME} file already exists",
                    fg="yellow",
                )
                if click.confirm("Do you want to replace it?"):
                    self._create_ini_file(board, ini_path, PROJECT_FILENAME)
                else:
                    click.secho("Abort!", fg="red")
        else:
            self._create_ini_file(board, ini_path, PROJECT_FILENAME)

    @staticmethod
    def _create_ini_file(board, ini_path, ini_name):
        click.secho(f"Creating {ini_name} file ...")
        with open(ini_path, "w", encoding="utf8") as file:
            config = configparser.ConfigParser()
            config.add_section("env")
            config.set("env", "board", board)
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

        # -- Update board
        self.board = board
        if not board:
            print("Error: invalid {PROJECT_FILENAME} project file")
            print("No 'board' field defined in project file")
            sys.exit(1)

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
