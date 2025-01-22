# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Utility functionality for apio click commands. """

import sys
from abc import ABC, abstractmethod

from configparser import ConfigParser
from pathlib import Path
from typing import Dict, Optional, Union, Any, List
from configobj import ConfigObj
from click import secho

# -- Apio projecto filename
APIO_INI = "apio.ini"

DEFAULT_TOP_MODULE = "main"

TOP_COMMENT = """\
APIO project configuration file. For details see
https://github.com/FPGAwars/apio/wiki/Project-configuration-file
"""

# -- Set of options every valid project should have.
REQUIRED_OPTIONS = {
    # -- The board name.
    "board",
}

# -- Set of additional options a project may have.
OPTIONAL_OPTIONS = {
    # -- The top module name. Default is 'main'.
    "top-module",
    # -- The default testbench name for 'apio sim'.
    "default-testbench",
    # -- Multi line list of verible options for 'apio format'
    "format-verible-options",
    # -- Additional option for the yosys synth command (inside the -p arg).
    "yosys-synth-extra-options",
}

# -- Set of all options a project may have.
ALL_OPTIONS = REQUIRED_OPTIONS | OPTIONAL_OPTIONS


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
                secho(
                    f"Error: missing option '{option}' in {APIO_INI}.",
                    fg="red",
                )
                sys.exit(1)

        # -- Check that there are no unknown options.
        supported_options = ALL_OPTIONS
        for option in self._options:
            if option not in supported_options:
                secho(f"Error: unknown project option '{option}'", fg="red")
                sys.exit(1)

        # -- Force 'board' to have the canonical name of the board.
        # -- This exists with an error message if the board is unknown.
        self._options["board"] = resolver.lookup_board_name(
            self._options["board"]
        )

        # -- If top-module was not specified, fill in the default value.
        if "top-module" not in self._options:
            self._options["top-module"] = DEFAULT_TOP_MODULE
            secho(
                "Project file has no 'top-module', "
                f"assuming '{DEFAULT_TOP_MODULE}'.",
                fg="yellow",
            )

    def get(self, option: str, default: Any = None) -> Union[str, Any]:
        """Lookup an option value by name. Returns default if not found."""
        # -- If this fails, this is a programming error.
        assert option in ALL_OPTIONS, f"Invalid project option: [{option}]"

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
        must be in ALL_OPTIONS."""

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
    file_path = project_dir / APIO_INI

    # -- Currently, apio.ini is still optional so we just warn.
    if not file_path.exists():
        secho(f"Error: missing project file {APIO_INI}.", fg="red")
        sys.exit(1)

    # -- Read and parse the file.
    parser = ConfigParser()
    parser.read(file_path)

    # -- Should contain an [env] section.
    if "env" not in parser.sections():
        secho(f"Error: {APIO_INI} has no [env] section.", fg="red")
        sys.exit(1)

    # -- Should not contain any other section.
    if len(parser.sections()) > 1:
        secho(
            f"Error: {APIO_INI} should contain only an [env] section.",
            fg="red",
        )
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
    ini_path = project_dir / APIO_INI

    # -- Error if apio.ini already exists.
    if ini_path.exists():

        secho(f"Error: the file {APIO_INI} already exists.", fg="red")
        sys.exit(1)

    # -- Construct and write the apio.ini file..
    secho(f"Creating {ini_path} file ...")

    config = ConfigObj(str(ini_path))
    config.initial_comment = TOP_COMMENT.split("\n")
    config["env"] = {}
    config["env"]["board"] = board_name
    config["env"]["top-module"] = top_module

    config.write()
    secho(
        f"The file '{ini_path}' was created successfully.",
        fg="green",
        bold=True,
    )
