# Apio project managment
import json


# ----------- Project default configurations

# -- Default FPGA board
DEFAULT_BOARD = 'icestick'

# -- Project file name
PROJECT_FILENAME = 'apio.ini'


class Project(object):

    def __init__(self, board):
        print('New APIO project')

        # -- Set the default board
        if board is None:
            self.board = DEFAULT_BOARD
        else:
            self.board = board

    def new(self):
        """Creates a new apio project file"""

        # -- Creates the project dictionary
        project = {"board": self.board}

        # -- Dump the project into the apio.ini file
        project_str = json.dumps(project)
        with open(PROJECT_FILENAME, 'w') as f:
            f.write(project_str)
        f.closed

        print("{} file created".format(PROJECT_FILENAME))

    def read(self):
        """Read the project config file"""

        with open(PROJECT_FILENAME, 'r') as f:
            project_str = f.read()

        project = json.loads(project_str)
        print("Project conf: {}".format(project))
