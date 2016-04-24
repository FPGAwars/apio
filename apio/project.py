# Apio project managment

# import os
import json

from os.path import isfile

# ----------- Project default configurations

# -- Default FPGA board
DEFAULT_BOARD = 'icestick'

# -- Project file name
PROJECT_FILENAME = 'apio.ini'


class Project(object):

    def __init__(self):
        self.board = DEFAULT_BOARD

    def new(self, board=DEFAULT_BOARD):
        """Creates a new apio project file"""

        if board is None:
            board = DEFAULT_BOARD

        # -- Creates the project dictionary
        project = {"board": board}

        # -- Dump the project into the apio.ini file
        project_str = json.dumps(project)
        with open(PROJECT_FILENAME, 'w') as f:
            f.write(project_str)
        f.closed

        print("{} file created".format(PROJECT_FILENAME))

    def read(self):
        """Read the project config file"""

        # -- If no project finel found, just return
        if not isfile(PROJECT_FILENAME):
            print("Warning: No apio.ini file")
            return

        # -- Open the project file
        with open(PROJECT_FILENAME, 'r') as f:
            project_str = f.read()

        # -- Decode the jsonj
        project = json.loads(project_str)

        # -- TODO: error checking

        # -- Update the board
        self.board = project['board']
