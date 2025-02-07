# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Utility functionality for apio click commands. """

import sys
from abc import ABC, abstractmethod

from configparser import ConfigParser
from pathlib import Path
from typing import Dict, Optional, Union, Any, List
from configobj import ConfigObj
from apio.common.apio_console import cout, cerror
from apio.common.apio_styles import INFO, SUCCESS


DEFAULT_TOP_MODULE = "main"

TOP_COMMENT = """\
APIO project configuration file. For details see
https://github.com/FPGAwars/apio/wiki/Project-configuration-file
"""

# -- The options docs here are formatted in the rich-text format of the
# -- python rich library. See apio_info.py to see how they are
# -- used.
BOARD_OPTION_DOC = """
The option 'board' specifies the board definition that is used by the \
project. The board ID must be one of the board IDs, such as 'alhambra-ii', \
that is listed by the command 'apio boards'.

Example:[code]
  board = alhambra-ii[/code]

Apio uses the board ID to determine information such as the FPGA part number \
and the programmer command to use to upload the design to the board.

Apio has resource files with definitions of boards, FPGAs, and programmers. \
If the project requires custom definitions, you can add custom \
'boards.jsonc', 'fpgas.jsonc', and 'programmers.jsonc' files in the project \
directory, and Apio will use them instead.
"""

TOP_MODULE_OPTION_DOC = """
The option 'top-module' specifies the name of the top module of the design. \
If 'top-module' is not specified, Apio assumes the default name 'main'; \
however, it is a good practice to always explicitly specify the top module.

Example:[code]
  top-module = my_main[/code]
"""

DEFAULT_TESTBENCH_DOC = """
The option 'default-testbench' is useful in projects that have more than \
a single testbench file, because it allows specifying the default testbench \
that will be simulated when the command 'apio sim' is run without a testbench \
argument.

Without this option, Apio will exit with an error message if the project \
contains more than one testbench file and a testbench was not specified in \
the 'apio sim' command.

Example:[code]
  default-testbench = my_module_tb.v[/code]
"""

FORMAT_VERIBLE_OPTIONS_DOC = """
The option 'format-verible-options' allows controlling the operation of the \
'apio format' command by specifying additional options to the underlying \
'verible' formatter.

Example:[code]
  format-verible-options =
      --column_limit=80
      --indentation_spaces=4[/code]

For the list of the Verible formatter options, run the command \
'apio raw -- verible-verilog-format --helpfull'
"""

YOSYS_SYNTH_EXTRA_OPTIONS_DOC = """
The option 'yosys-synth-extra-options' allows adding options to the \
yosys synth command. In the example below, it adds the option '-dsp', \
which enables for some FPGAs the use of DSP cells to implement multiply \
operations. This is an advanced and esoteric option that is typically \
not needed.

Example:[code]
  yosys-synth-extra-options = -dsp[/code]
"""

OPTIONS = {
    # -- The board name.
    "board": BOARD_OPTION_DOC,
    # -- The top module name. Default is 'main'.
    "top-module": TOP_MODULE_OPTION_DOC,
    # -- The default testbench name for 'apio sim'.
    "default-testbench": DEFAULT_TESTBENCH_DOC,
    # -- Multi line list of verible options for 'apio format'
    "format-verible-options": FORMAT_VERIBLE_OPTIONS_DOC,
    # -- Additional option for the yosys synth command (inside the -p arg).
    "yosys-synth-extra-options": YOSYS_SYNTH_EXTRA_OPTIONS_DOC,
}

# -- The subset of the options in OPTIONS that are required.
REQUIRED_OPTIONS = {
    "board",
}


# pylint: disable=too-few-public-methods
class ProjectResolver(ABC):
    """An abstract class with services that are needed for project validation.
    Generally speaking it provides a subset of the functionality of ApioContext
    and we use it to avoid a cyclic import between Project and ApioContext.
    """

    @abstractmethod
    def lookup_board_name(self, board: str) -> str:
        """Similar to ApioContext.lookup_board()"""


class Project:
    """An instance of this class holds the information from the project's
    apio.ini file.
    """

    def __init__(self, options: Dict[str, str], resolver: ProjectResolver):
        """Construct with given {name, value} options dict. To validate the
        option call validate()."""
        self._options = options
        self._validate(resolver)

    def __str__(self):
        """For debugging."""
        lines = ["Project options:"]
        for name, val in self._options.items():
            lines.append(f"  {name} = {val}")
        return "\n".join(lines)

    def _validate(self, resolver: ProjectResolver):
        """Validates the options. Exists with an error message on any problem.
        'resolver' is an object that allows to validate the board name and
        to set the board option to a new board name if a legacy one was
        specified.
        """

        # -- Check that all the required options are present.
        for option in REQUIRED_OPTIONS:
            if option not in self._options:
                cerror(f"Missing option '{option}' in apio.ini.")
                sys.exit(1)

        # -- Check that there are no unknown options.
        for option in self._options:
            if option not in OPTIONS:
                cerror(f"Unknown project option '{option}'")
                sys.exit(1)

        # -- Force 'board' to have the canonical name of the board.
        # -- This exists with an error message if the board is unknown.
        self._options["board"] = resolver.lookup_board_name(
            self._options["board"]
        )

        # -- If top-module was not specified, fill in the default value.
        if "top-module" not in self._options:
            self._options["top-module"] = DEFAULT_TOP_MODULE
            cout(
                "Project file has no 'top-module', "
                f"assuming '{DEFAULT_TOP_MODULE}'.",
                style=INFO,
            )

    def get(self, option: str, default: Any = None) -> Union[str, Any]:
        """Lookup an option value by name. Returns default if not found."""
        # -- If this fails, this is a programming error.
        assert option in OPTIONS, f"Invalid project option: [{option}]"

        # -- Lookup with default
        return self._options.get(option, default)

    def __getitem__(self, option: str) -> Optional[str]:
        """Lookup an option value by name using the [] operator. Returns
        None if not found."""
        return self.get(option, None)

    def get_as_lines_list(
        self, option: str, default: Any = None
    ) -> Union[List[str], Any]:
        """Lookup an option value that has a line list format. Returns
        the list of non empty lines or default if no value. Option
        must be in OPTIONS."""

        # -- Get the raw value.
        values = self.get(option, None)

        # -- If not found, return default
        if values is None:
            return default

        # -- Break the values to a list of lines. Each line is already
        # -- right and left of white space by configparser and comments
        # -- are removed.
        values = values.split("\n")

        # -- Select the non empty items.
        values = [x for x in values if x]

        return values


def load_project_from_file(
    project_dir: Path, resolver: ProjectResolver
) -> Project:
    """Read project file from given project dir. Returns None if file
    does not exists. Exits on any error. Otherwise creates adn
    return an Project with the values. To validate the project object
    call its validate() method."""

    # -- Construct the apio.ini path.
    file_path = project_dir / "apio.ini"

    # -- Currently, apio.ini is still optional so we just warn.
    if not file_path.exists():
        cerror("Missing project file apio.ini.")
        sys.exit(1)

    # -- Read and parse the file.
    parser = ConfigParser()
    parser.read(file_path)

    # -- Should contain an [env] section.
    if "env" not in parser.sections():
        cerror("The file apio.ini has no [env] section.")
        sys.exit(1)

    # -- Should not contain any other section.
    if len(parser.sections()) > 1:
        cerror("The file apio.ini should contain only an [env] section.")
        sys.exit(1)

    # -- Collect the name/value pairs.
    options = {}
    for name, val in parser.items("env"):
        options[name] = val

    # -- Construct the Project object. Its constructor validates the options.
    return Project(options, resolver)


def create_project_file(
    project_dir: Path,
    board_name: str,
    top_module: str,
):
    """Creates a new apio project file. Exits on any error."""

    # -- Construct the path
    ini_path = project_dir / "apio.ini"

    # -- Error if apio.ini already exists.
    if ini_path.exists():
        cerror("The file apio.ini already exists.")
        sys.exit(1)

    # -- Construct and write the apio.ini file..
    cout(f"Creating {ini_path} file ...")

    config = ConfigObj(str(ini_path))
    config.initial_comment = TOP_COMMENT.split("\n")
    config["env"] = {}
    config["env"]["board"] = board_name
    config["env"]["top-module"] = top_module

    config.write()
    cout(f"The file '{ini_path}' was created successfully.", style=SUCCESS)
