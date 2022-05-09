# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Juan González, Jesús Arroyo
# -- Licence GPLv2

import sys
import json
from os.path import isfile
import click

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

from apio import util
from apio.resources import Resources

PROJECT_FILENAME = "apio.ini"


class Project:
    def __init__(self):
        self.board = None

    def create_sconstruct(self, project_dir="", arch=None, sayyes=False):
        """Creates a default SConstruct file"""

        project_dir = util.check_dir(project_dir)

        sconstruct_name = "SConstruct"
        sconstruct_path = util.safe_join(project_dir, sconstruct_name)
        local_sconstruct_path = util.safe_join(
            util.get_folder("resources"), arch, sconstruct_name
        )

        if isfile(sconstruct_path):
            # -- If sayyes, skip the question
            if sayyes:
                self._copy_sconstruct_file(
                    sconstruct_name, sconstruct_path, local_sconstruct_path
                )
            else:
                click.secho(
                    "Warning: {} file already exists".format(sconstruct_name),
                    fg="yellow",
                )

                if click.confirm("Do you want to replace it?"):
                    self._copy_sconstruct_file(
                        sconstruct_name, sconstruct_path, local_sconstruct_path
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

        ini_path = util.safe_join(project_dir, PROJECT_FILENAME)

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
            config = ConfigParser.ConfigParser()
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
        with open(sconstruct_path, "w", encoding="utf8") as sconstruct:
            with open(
                local_sconstruct_path, "r", encoding="utf8"
            ) as local_sconstruct:
                sconstruct.write(local_sconstruct.read())
                click.secho(
                    "File '{sconstruct_name}' has been successfully created!",
                    fg="green",
                )

    def read(self):
        """Read the project config file"""

        # -- If no project finel found, just return
        if not isfile(PROJECT_FILENAME):
            print("Info: No {PROJECT_FILENAME} file")
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
    def _read_board():
        board = ""

        # -- Read config file: old JSON format
        with open(PROJECT_FILENAME, "r", encoding="utf8") as file:
            try:
                data = json.loads(file.read())
                board = data.get("board")
            except Exception:
                pass

        # -- Read config file: new CFG format
        if board == "":
            try:
                config = ConfigParser.ConfigParser()
                config.read(PROJECT_FILENAME)
                board = config.get("env", "board")
            except Exception:
                print("Error: invalid {PROJECT_FILENAME} project file")
                sys.exit(1)

        return board
