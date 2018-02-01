# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Juan González, Jesús Arroyo
# -- Licence GPLv2

import sys
import json
import click

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

from os.path import isfile

from apio import util
from apio.resources import Resources

PROJECT_FILENAME = 'apio.ini'


class Project(object):

    def __init__(self):
        self.board = None

    def create_sconstruct(self, project_dir='', sayyes=False):
        """Creates a default SConstruct file"""

        project_dir = util.check_dir(project_dir)

        sconstruct_name = 'SConstruct'
        sconstruct_path = util.safe_join(project_dir, sconstruct_name)
        local_sconstruct_path = util.safe_join(
            util.get_folder('resources'), sconstruct_name)

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

        project_dir = util.check_dir(project_dir)

        ini_path = util.safe_join(project_dir, PROJECT_FILENAME)

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
        click.secho('Creating {} file ...'.format(ini_name))
        with open(ini_path, 'w') as file:
            config = ConfigParser.ConfigParser()
            config.add_section('env')
            config.set('env', 'board', board)
            config.write(file)
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
            print('Info: No {} file'.format(PROJECT_FILENAME))
            return

        # -- Read stored board
        board = self._read_board()

        # -- Update board
        self.board = board
        if not board:
            print('Error: Invalid {} project file'.format(
                PROJECT_FILENAME))
            print('No \'board\' field defined in project file')
            sys.exit(1)

    def _read_board(self):
        board = ''

        # -- Read config file: old JSON format
        with open(PROJECT_FILENAME, 'r') as f:
            try:
                data = json.loads(f.read())
                board = data.get('board')
            except Exception:
                pass

        # -- Read config file: new CFG format
        if board == '':
            try:
                config = ConfigParser.ConfigParser()
                config.read(PROJECT_FILENAME)
                board = config.get('env', 'board')
            except Exception:
                print('Error: Invalid {} project file'.format(
                    PROJECT_FILENAME))
                sys.exit(1)

        return board
