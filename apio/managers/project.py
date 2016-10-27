# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Juan González, Jesús Arroyo
# -- Licence GPLv2

import sys
import json
import click

from os.path import isfile, join, dirname

from apio.resources import Resources

PROJECT_FILENAME = 'apio.ini'


class Project(object):

    def __init__(self):
        self.board = None

    def create_sconstruct(self, project_dir='', sayyes=False):
        """Creates a default SConstruct file"""

        if project_dir is None:
            project_dir = ''

        sconstruct_name = 'SConstruct'
        sconstruct_path = join(project_dir, sconstruct_name)
        local_sconstruct_path = join(
            dirname(__file__), '..', 'resources', sconstruct_name)

        if isfile(sconstruct_path):
            # -- If sayyes, skip the question
            if sayyes:
                self._copy_sconstruct_file(sconstruct_name, sconstruct_path,
                                           local_sconstruct_path)
            else:
                click.secho(
                    'Warning: {} file already exists'.format(sconstruct_name),
                    fg='yellow')

                if click.confirm('Do you want to replace it?'):
                    self._copy_sconstruct_file(sconstruct_name,
                                               sconstruct_path,
                                               local_sconstruct_path)
                else:
                    click.secho('Abort!', fg='red')

        else:
            self._copy_sconstruct_file(sconstruct_name, sconstruct_path,
                                       local_sconstruct_path)

    def create_ini(self, board, project_dir='', sayyes=False):
        """Creates a new apio project file"""

        if project_dir is None:
            project_dir = ''

        ini_path = join(project_dir, PROJECT_FILENAME)

        # Check board
        boards = Resources().boards
        if board not in boards.keys():
            click.secho(
                'Error: No such board \'{}\''.format(board),
                fg='red')
            sys.exit(1)

        if isfile(ini_path):
            # -- If sayyes, skip the question
            if sayyes:
                self._create_ini_file(board, ini_path, PROJECT_FILENAME)
            else:
                click.secho(
                    'Warning: {} file already exists'.format(PROJECT_FILENAME),
                    fg='yellow')
                if click.confirm('Do you want to replace it?'):
                    self._create_ini_file(board, ini_path, PROJECT_FILENAME)
                else:
                    click.secho('Abort!', fg='red')
        else:
            self._create_ini_file(board, ini_path, PROJECT_FILENAME)

    def _create_ini_file(self, board, ini_path, ini_name):
        # Creates the project dictionary
        project = {"board": board}

        # Dump the project into the apio.ini file
        project_str = json.dumps(project)

        click.secho('Creating {} file ...'.format(ini_name))
        with open(ini_path, 'w') as file:
            file.write(project_str)
            click.secho(
                'File \'{}\' has been successfully created!'.format(
                    ini_name),
                fg='green')

    def _copy_sconstruct_file(self, sconstruct_name,
                              sconstruct_path, local_sconstruct_path):
        click.secho('Creating {} file ...'.format(sconstruct_name))
        with open(sconstruct_path, 'w') as sconstruct:
            with open(local_sconstruct_path, 'r') as local_sconstruct:
                sconstruct.write(local_sconstruct.read())
                click.secho(
                    'File \'{}\' has been successfully created!'.format(
                        sconstruct_name),
                    fg='green')

    def read(self):
        """Read the project config file"""

        # -- If no project finel found, just return
        if not isfile(PROJECT_FILENAME):
            print("Info: No apio.ini file")
            return

        # -- Open the project file
        with open(PROJECT_FILENAME, 'r') as f:
            project_str = f.read()

        # -- Decode the jsonj
        try:
            project = json.loads(project_str)
        except:
            print("Error: Invalid {} project file".format(PROJECT_FILENAME))
            sys.exit(1)

        # -- TODO: error checking

        # -- Update the board
        try:
            self.board = project['board']
        except:
            print("Error: Invalid {} project file".format(PROJECT_FILENAME))
            print("No 'board' field defined in project file")
            sys.exit(1)
