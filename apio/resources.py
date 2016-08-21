#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import click

# --------- Configuration

BOARDS_FILENAME = 'boards.json'
FPGAS_FILENAME = 'fpgas.json'
PACKAGES_FILENAME = 'packages.json'

BOARDS_MSG = """
Use `apio init --board <boardname>` for creating a new apio """ \
"""proyect for that board"""


class Resources(object):

    def __init__(self):
        self.boards = None
        self.fpgas = None
        self.packages = None

        # -- Get config dir
        config_dir = os.path.join(os.path.dirname(__file__), 'resources')

        # -- Get the fully boards_filename with path
        boards_filename = os.path.join(config_dir, BOARDS_FILENAME)
        fpgas_filename = os.path.join(config_dir, FPGAS_FILENAME)
        packages_filename = os.path.join(config_dir, PACKAGES_FILENAME)

        # -- Load the boards file
        with open(boards_filename, 'r') as f:
            boards_str = f.read()
            self.boards = json.loads(boards_str)

        # -- Load the fpgas file
        with open(fpgas_filename, 'r') as f:
            fpgas_str = f.read()
            self.fpgas = json.loads(fpgas_str)

        # -- Load the packages file
        with open(packages_filename, 'r') as f:
            packages_str = f.read()
            self.packages = json.loads(packages_str)

    def list_boards(self):
        """Return a list with all the supported boards"""

        # -- Print table
        click.echo('Supported boards:\n')

        BOARDLIST_TPL = ('{name:22} {fpga:20} {type:<5} {size:<5} {pack:<10}')
        terminal_width, _ = click.get_terminal_size()

        click.echo('-' * terminal_width)
        click.echo(BOARDLIST_TPL.format(
            name=click.style('Name', fg='cyan'), fpga='FPGA', type='Type',
            size='Size', pack='Pack'))
        click.echo('-' * terminal_width)

        for board in self.boards:
            fpga = self.boards[board]['fpga']
            click.echo(BOARDLIST_TPL.format(
                name=click.style(board, fg='cyan'), fpga=fpga, type=self.fpgas[fpga]['type'],
                size=self.fpgas[fpga]['size'], pack=self.fpgas[fpga]['pack']))

        click.secho(BOARDS_MSG, fg='green')
