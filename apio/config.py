#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import click

# --------- Configuration

# -- Boards filename
BOARDS_FILENAME = 'boards.json'

EXAMPLE_MSG = """
Use `apio init --board <boardname>` for creating a new apio """ \
"""proyect for that board"""


class Boards(object):

    def __init__(self):
        self.boards = None

    def list(self):
        """Return a list with all the supported boards"""

        # -- Get config dir
        config_dir = os.path.join(os.path.dirname(__file__), 'config')

        # -- Get the fully boards_filename with path
        boards_filename = os.path.join(config_dir, BOARDS_FILENAME)

        # -- Open the boards file
        with open(boards_filename, 'r') as f:
            boards_str = f.read()

        # -- Decode the json
        self.boards = json.loads(boards_str)

        # -- Print table
        click.echo('Supported boards:\n')

        BOARDLIST_TPL = ('{name:20} {type:<5} {size:<5} {pack:<10}')
        terminal_width, _ = click.get_terminal_size()

        click.echo('-' * terminal_width)
        click.echo(BOARDLIST_TPL.format(
            name=click.style('Name', fg='cyan'), type='Type',
            size='Size', pack='Pack'))
        click.echo('-' * terminal_width)

        for board in self.boards:
            click.echo(BOARDLIST_TPL.format(
                name=click.style(board, fg='cyan'), type=self.boards[board]['type'],
                size=self.boards[board]['size'], pack=self.boards[board]['pack']))

        click.secho(EXAMPLE_MSG, fg='green')
