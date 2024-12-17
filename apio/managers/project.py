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
from typing import Dict, Optional
from configobj import ConfigObj
import click

# -- Apio projecto filename
APIO_INI = "apio.ini"

DEFAULT_TOP_MODULE = "main"

TOP_COMMENT = """\
APIO project configuration file. For details see
https://github.com/FPGAwars/apio/wiki/Project-configuration-file
"""

# -- Set of options every valid project should have.
REQUIRED_OPTIONS = {"board"}

# -- Set of additional options a project may have.
OPTIONAL_OPTIONS = {"top-module"}

# -- Set of all options a project may have.
ALL_OPTIONS = REQUIRED_OPTIONS | OPTIONAL_OPTIONS


# pylint: disable=too-few-public-methods
class ProjectResolver(ABC):
    """An abstract class with services that are needed for project validation.
    Generally speaking it provides a subset of the functionality of ApioContext
    and we use it to avoid a cyclic import between Project and ApioContext.
    """

    @abstractmethod
    def lookup_board_id(self, board: str) -> str:
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
        'resolver' is an object that allows to validate the board id and
        to set the board option to a new board id if a legacy one was
        specified.
        """

        # -- Check that all the required options are present.
        for option in REQUIRED_OPTIONS:
            if option not in self._options:
                click.secho(
                    f"Error: missing option '{option}' in {APIO_INI}.",
                    fg="red",
                )
                sys.exit(1)

        # -- Check that there are no unknown options.
        supported_options = ALL_OPTIONS
        for option in self._options:
            if option not in supported_options:
                click.secho(
                    f"Error: unknown project option '{option}'", fg="red"
                )
                sys.exit(1)

        # -- Force 'board' to have the canonical id of the board.
        # -- This exists with an error message if the board is unknown.
        self._options["board"] = resolver.lookup_board_id(
            self._options["board"]
        )

    def __getitem__(self, option: str) -> Optional[str]:
        # -- If this fails, this is a programming error.
        assert option in ALL_OPTIONS, f"Invalid project option: [{option}]"

        # -- Lookup with default
        return self._options.get(option, None)


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
        click.secho(f"Info: Project has no {APIO_INI} file.", fg="yellow")
        return None

    # -- Read and parse the file.
    parser = ConfigParser()
    parser.read(file_path)

    # -- Should contain an [env] section.
    if "env" not in parser.sections():
        click.secho(f"Error: {APIO_INI} has no [env] section.", fg="red")
        sys.exit(1)

    # -- Should not contain any other section.
    if len(parser.sections()) > 1:
        click.secho(
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
    board_id: str,
    top_module: str,
    sayyes: bool = False,
) -> bool:
    """Creates a new apio project file. Returns True if ok.
    'board_id' is assumed to be the canonical if of a supported board
    (caller should validate)"""

    # -- Construct the path
    ini_path = project_dir / APIO_INI

    # -- If the ini file already exists, ask if it's ok to delete.
    if ini_path.is_file():

        # -- Warn the user, unless the flag sayyes is active
        if not sayyes:
            click.secho(
                f"Warning: {APIO_INI} file already exists",
                fg="yellow",
            )

            # -- Ask for confirmation
            replace = click.confirm("Do you want to replace it?")

            # -- User say: NO! --> Abort
            if not replace:
                click.secho("Abort!", fg="red")
                return False

    # -- Create the apio.ini from scratch.
    click.secho(f"Creating {ini_path} file ...")
    config = ConfigObj(str(ini_path))
    config.initial_comment = TOP_COMMENT.split("\n")
    config["env"] = {}
    config["env"]["board"] = board_id
    config["env"]["top-module"] = top_module
    config.write()
    click.secho(
        f"The file '{ini_path}' was created successfully.\n"
        "Run the apio clean command for project consistency.",
        fg="green",
    )
    return True


def modify_project_file(
    project_dir: Path,
    board: Optional[str],
    top_module: Optional[str],
) -> bool:
    """Update the current ini file with the given optional parameters.
    Returns True if ok. Board is assumed to be None or a canonical id of an
    exiting board (caller should validate)"""

    # -- construct the file path.
    ini_path = project_dir / APIO_INI

    # -- Check if the apio.ini file exists
    if not ini_path.is_file():
        click.secho(
            f"Error: '{ini_path}' not found. You should create it first.\n"
            "see 'apio create -h' for more details.",
            fg="red",
        )
        return False

    # -- Read the current apio.ini file
    config = ConfigObj(str(ini_path))

    # -- Set specified fields.
    if board:
        config["env"]["board"] = board

    if top_module:
        config["env"]["top-module"] = top_module

    # -- Write the apio ini file
    config.write()

    click.secho(
        f"File '{ini_path}' was modified successfully.\n"
        f"Run the apio clean command for project consistency.",
        fg="green",
    )
    return True
