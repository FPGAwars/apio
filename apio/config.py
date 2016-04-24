#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

# --------- Configuration

# -- Boards filename
BOARDS_FILENAME = 'boards.json'


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

        print('')
        print("Supported boards:\n")
        for board in self.boards:
            print("> {}".format(board))

        print('')
        print("Use apio init --board <boardname> for creating a new apio" +
              " proyect for that board")
