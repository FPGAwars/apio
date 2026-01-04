# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Utility functionality for apio click commands."""

import sys
import re
from dataclasses import dataclass
import configparser
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Optional, Union, Any, List
from configobj import ConfigObj
from apio.utils import util
from apio.common.apio_console import cout, cerror, cwarning
from apio.common.apio_styles import INFO, SUCCESS, EMPH2


DEFAULT_TOP_MODULE = "main"

ENV_NAME_REGEX = re.compile(r"^[a-z][a-z0-9-]*$")

ENV_NAME_HINT = (
    "Env names should start with a-z, "
    "followed by any number of a-z, 0-9, and '-'."
)

TOP_COMMENT = """\
APIO project configuration file.
For details see https://fpgawars.github.io/apio/docs/project-file
"""

# -- Apio options. These are the options that appear in the [apio] section.
# -- They are not subject to inheritance and resolution.


APIO_OPTIONS = [
    # -- Selecting the env to use if not overridden in command line. Otherwise
    # -- the first env is the default.
    "default-env",
]


@dataclass(frozen=True)
class EnvOptionSpec:
    """Specifies a single apio.ini env option which can appear in an
    env section or the common section."""

    name: str
    is_required: bool = False
    is_list: bool = False


# -- Specification of the env options which can appear in env sections
# -- or the common section of apio.ini.
ENV_OPTIONS_SPEC = {
    "board": EnvOptionSpec(
        name="board",
        is_required=True,
    ),
    "top-module": EnvOptionSpec(
        name="top-module",
        is_required=True,
    ),
    "default-testbench": EnvOptionSpec(
        name="default-testbench",
    ),
    "defines": EnvOptionSpec(
        name="defines",
        is_list=True,
    ),
    "format-verible-options": EnvOptionSpec(
        name="format-verible-options",
        is_list=True,
    ),
    "programmer-cmd": EnvOptionSpec(
        name="programmer-cmd",
    ),
    "yosys-synth-extra-options": EnvOptionSpec(
        name="yosys-synth-extra-options",
        is_list=True,
    ),
    "nextpnr-extra-options": EnvOptionSpec(
        name="nextpnr-extra-options",
        is_list=True,
    ),
    "constraint-file": EnvOptionSpec(
        name="constraint-file",
    ),
}


class Project:
    """An instance of this class holds the information from the project's
    apio.ini file.
    """

    def __init__(
        self,
        *,
        apio_section: Optional[Dict[str, str]],
        common_section: Optional[Dict[str, str]],
        env_sections: Dict[str, Dict[str, str]],
        env_arg: Optional[str],
        boards: Dict[str, Dict],
    ):
        """Construct the project with information from apio.ini, command
        line arg, and boards resources."""

        # pylint: disable=too-many-arguments

        if util.is_debug(1):
            cout()
            cout("Parsed [apio] section:", style=EMPH2)
            cout(f"  {apio_section}\n")
            cout("Parsed [common] section:", style=EMPH2)
            cout(f"  {common_section}\n")
            for env_name, section_options in env_sections.items():
                cout(f"Parsed [env:{env_name}] section:", style=EMPH2)
                cout(f"{section_options}\n")

        # -- Validate the format of the env_arg value.
        if env_arg is not None:
            if not ENV_NAME_REGEX.match(env_arg):
                cerror(f"Invalid --env value '{env_arg}'.")
                cout(ENV_NAME_HINT, style=INFO)
                sys.exit(1)

        # -- Patch legacy board ids in the common and env sections.
        Project._patch_legacy_board_id(common_section, boards)
        for section_options in env_sections.values():
            Project._patch_legacy_board_id(section_options, boards)

        # -- Validate the apio.ini sections. We prefer to perform as much
        # -- validation as possible before we expand the env because the env
        # -- expansion may hide some options.
        Project._validate_all_sections(
            apio_section=apio_section,
            common_section=common_section,
            env_sections=env_sections,
            boards=boards,
        )

        # -- Keep the names of all envs
        self.env_names = list(env_sections.keys())

        # -- Determine the name of the active env.
        self.env_name = Project._determine_default_env_name(
            apio_section, env_sections, env_arg
        )

        # -- Expand and selected env options. This is also patches default
        # -- values and validates the results.
        self.env_options: Dict[str, Union[str, List[str]]] = (
            Project._parse_env_options(
                env_name=self.env_name,
                common_section=common_section,
                env_sections=env_sections,
            )
        )
        if util.is_debug(1):
            cout("Selected env name:", style=EMPH2)
            cout(f"  {self.env_name}\n")
            cout("Expanded env options:", style=EMPH2)
            cout(f"  {self.env_options}\n")

    @staticmethod
    def _patch_legacy_board_id(
        section_options: Dict[str, Dict[str, str]], boards: Dict[str, Dict]
    ) -> Optional[str]:
        """Temporary patching of old board ids to new in an env or common
        section. If there is a "board" option with a legacy board id,
        then change it to the board's canonical name. Otherwise, leave the
        options as are."""

        # -- Get the value of the "board" option.
        board_id = section_options.get("board", None)

        # -- Nothing to do if no "board" option.
        if board_id is None:
            return

        # -- Nothing to do if board_id is in the boards dict. It's
        # -- a good (new style) board id.
        if board_id in boards:
            return

        # -- Iterate the boards and if board_id matches the legacy name of
        # -- a board, change the "board" option to the canonical name of that
        # -- board.
        for canonical_id, board_info in boards.items():
            if board_id == board_info.get("legacy-name", None):
                section_options["board"] = canonical_id
                cwarning(
                    f"'Board {board_id}' was renamed to '{canonical_id}'. "
                    "Please update apio.ini."
                )
                return

    @staticmethod
    def _validate_all_sections(
        apio_section: Optional[Dict[str, str]],
        common_section: Optional[Dict[str, str]],
        env_sections: Dict[str, Dict[str, str]],
        boards: Dict[str, Dict],
    ):
        """Validate the parsed apio.ini sections."""

        # -- Validate the common section.
        Project._validate_env_section("[common]", common_section, boards)

        # -- Validate the env sections.
        if not env_sections:
            cerror(
                "Project file 'apio.ini' should have at least one "
                "[env:name] section."
            )
            sys.exit(1)

        for env_name, section_options in env_sections.items():
            # -- Validate env name format.
            if not ENV_NAME_REGEX.match(env_name):
                cerror(f"Invalid env name '{env_name}' in apio.ini.")
                cout(ENV_NAME_HINT, style=INFO)
                sys.exit(1)
            # -- Validate env section options.
            Project._validate_env_section(
                f"[env:{env_name}]", section_options, boards
            )

        # -- Validate the apio section. At this point the env_sections are
        # -- already validated.
        Project._validate_apio_section(apio_section, env_sections)

    @staticmethod
    def _validate_apio_section(
        apio_section: Dict[str, str], env_sections: Dict[str, Dict[str, str]]
    ):
        """Validate the [apio] section. 'env_sections' are assumed to be
        validated."""

        # -- Look for unknown options.
        for option in apio_section:
            if option not in APIO_OPTIONS:
                cerror(
                    f"Unknown option '{option} in [apio] section of apio.ini'"
                )
                sys.exit(1)

        # -- If 'default-env' option exists, verify the env name is valid and
        # -- and the name exists.
        default_env_name = apio_section.get("default-env", None)
        if default_env_name:
            # -- Validate env name format.
            if not ENV_NAME_REGEX.match(default_env_name):
                cerror(
                    f"Invalid default env name '{default_env_name}' "
                    "in apio.ini."
                )
                cout(ENV_NAME_HINT, style=INFO)
                sys.exit(1)
            # -- Make sure the env exists.
            if default_env_name not in env_sections:
                cerror(f"Env '{default_env_name}' not found in apio.ini.")
                cout(
                    f"Expecting an env section '{default_env_name}' "
                    "in apio.ini",
                    style=INFO,
                )
                sys.exit(1)

    @staticmethod
    def _validate_env_section(
        section_title: str,
        section_options: Dict[str, str],
        boards: Dict[str, Dict],
    ):
        """Validate the options of a section that contains env options. This
        includes the sections [env:*] and [common]."""

        # -- Check that there are no unknown options.
        for option in section_options:
            if option not in ENV_OPTIONS_SPEC:
                cerror(
                    f"Unknown option '{option}' in {section_title} "
                    "section of apio.ini."
                )
                sys.exit(1)

        # -- If 'board' option exists, verify that the board exists.
        board_id = section_options.get("board", None)
        if board_id is not None and board_id not in boards:
            cerror(f"Unknown board id '{board_id}' in apio.ini.")
            sys.exit(1)

    @staticmethod
    def _determine_default_env_name(
        apio_section: Dict[str, str],
        env_sections: Dict[str, Dict[str, str]],
        env_arg: Optional[str],
    ) -> str:
        """Determines the active env name. Sections are assumed to be
        validated. 'env_arg' is the value of the optional command line --env
        which allows the user to select the env."""
        # -- Priority #1 (highest): User specified env name in the command.
        env_name = env_arg

        # -- Priority #2: The optional default-env option in the
        # -- [apio] section.
        if env_name is None:
            env_name = apio_section.get("default-env", None)

        # -- Priority #3 (lowest): Picking the first env defined in apio.ini.
        # -- Note that the envs order is preserved in env_sections.
        if env_name is None:
            # -- The env sections preserve the order in apio.ini.
            env_name = list(env_sections.keys())[0]

        # -- Error if the env doesn't exist.
        if env_name not in env_sections:
            cerror(f"Env '{env_name}' not found in apio.ini.")
            cout(
                f"Expecting an env section '[env:{env_name}] in apio.ini",
                style=INFO,
            )
            sys.exit(1)

        # -- All done.
        return env_name

    @staticmethod
    def _parse_env_options(
        env_name: str,
        common_section: Dict[str, str],
        env_sections: Dict[str, Dict[str, Union[str, List[str]]]],
    ) -> Dict[str, Union[str, List[str]]]:
        """Expand the options of given env name. The given common and envs
        sections are already validate. String options are returned as strings
        and list options are returned as list of strings.
        """

        # -- Select the env section by name.
        env_section = env_sections[env_name]

        # -- Create an empty result dict.
        # -- We will insert to it the relevant options by the oder they appear
        # -- in apio.ini.
        result: Dict[str, Union[str, List[str]]] = {}

        # -- Add common options that are not in env section
        for name, val in common_section.items():
            if name not in env_section:
                result[name] = val

        # -- Add all the options from the env section.
        for name, val in env_section.items():
            result[name] = val

        # -- check that all the required options exist.
        for option_spec in ENV_OPTIONS_SPEC.values():
            if option_spec.is_required and option_spec.name not in result:
                cerror(
                    f"Missing required option '{option_spec.name}' "
                    f"for env '{env_name}'."
                )
                sys.exit(1)

        # -- Convert the list options from strings to list.
        for name, str_val in result.items():
            option_spec: EnvOptionSpec = ENV_OPTIONS_SPEC.get(name)
            if option_spec.is_list:
                list_val = str_val.split("\n")
                # -- Select the non empty items.
                list_val = [x for x in list_val if x]
                result[name] = list_val

        return result

    def get_str_option(
        self, option: str, default: Any = None
    ) -> Union[str, Any]:
        """Lookup an env option value by name. Returns default if not found."""

        # -- If this fails, this is a programming error.
        option_spec: EnvOptionSpec = ENV_OPTIONS_SPEC.get(option, None)
        assert option_spec, f"Invalid env option: [{option}]"
        assert not option_spec.is_list, f"Not a simple str option: {option}"

        # -- Lookup with default
        value = self.env_options.get(option, None)

        if value is None:
            return default

        assert isinstance(value, str)
        return value

    def get_list_option(
        self, option: str, default: Any = None
    ) -> Union[List[str], Any]:
        """Lookup an env option value that has a line list format. Returns
        the list of non empty lines or default if no value. Option
        must be in OPTIONS."""

        # -- If this fails, this is a programming error.
        option_spec: EnvOptionSpec = ENV_OPTIONS_SPEC.get(option, None)
        assert option_spec, f"Invalid env option: [{option}]"
        assert option_spec.is_list, f"Not a list option: {option}"

        # -- Get the option values, it's is expected to be a list of str.
        values_list = self.env_options.get(option, None)

        # -- If not found, return default
        if values_list is None:
            return default

        # -- Return the list
        assert isinstance(values_list, list), values_list
        return values_list


def load_project_from_file(
    project_dir: Path, env_arg: Optional[str], boards: Dict[str, Dict]
) -> Project:
    """Read project file from given project dir. Returns None if file
    does not exists. Exits on any error. Otherwise creates adn
    return an Project with the values. To validate the project object
    call its validate() method."""

    # -- Construct the apio.ini path.
    file_path = project_dir / "apio.ini"

    # -- Currently, apio.ini is still optional so we just warn.
    if not file_path.exists():
        cerror(
            "Missing project file apio.ini.",
            f"Expected a file at '{file_path.absolute()}'",
        )
        sys.exit(1)

    # -- Read and parse the file.
    # -- By using OrderedDict we cause the parser to preserve the order of
    # -- options in a section. The order of sections is already preserved by
    # -- default.
    parser = configparser.ConfigParser(dict_type=OrderedDict)
    try:
        parser.read(file_path)
    except configparser.Error as e:
        cerror(e)
        sys.exit(1)

    # -- Iterate and collect the sections in the order they appear in
    # -- the apio.ini file. Section names are guaranteed to be unique with
    # -- no duplicates.
    sections_names = parser.sections()

    apio_section = None
    common_section = None
    env_sections = {}

    for section_name in sections_names:
        # -- Handle the [apio[ section.]]
        if section_name == "apio":
            if common_section or env_sections:
                cerror("The [apio] section must be the first section.")
                sys.exit(1)
            apio_section = dict(parser.items(section_name))
            continue

        # -- Handle the [common] section.
        if section_name == "common":
            if env_sections:
                cerror("The [common] section must be before [env:] sections.")
                sys.exit(1)
            common_section = dict(parser.items(section_name))
            continue

        # TODO: Remove this option after this is released.
        # -- Handle the legacy [env] section.
        if section_name == "env" and len(sections_names) == 1:
            # env_sections["default"] = parser.items(section_name)
            cwarning(
                "Apio.ini has a legacy [env] section. "
                "Please rename it to [env:default]."
            )
            env_sections["default"] = dict(parser.items(section_name))
            continue

        # -- Handle the [env:env-name] sections.
        tokes = section_name.split(":")
        if len(tokes) == 2 and tokes[0] == "env":
            env_name = tokes[1]
            env_sections[env_name] = dict(parser.items(section_name))
            continue

        # -- Handle unknown section name.
        cerror(f"Invalid section name '{section_name}' in apio.ini.")
        cout(
            "The valid section names are [apio], [common], and [env:env-name]",
            style=INFO,
        )
        sys.exit(1)

    # -- Construct the Project object. Its constructor validates the options.
    return Project(
        apio_section=apio_section or {},
        common_section=common_section or {},
        env_sections=env_sections,
        env_arg=env_arg,
        boards=boards,
    )


def create_project_file(
    project_dir: Path,
    board_id: str,
    top_module: str,
):
    """Creates a new basic apio project file. Exits on any error."""

    # -- Construct the path
    ini_path = project_dir / "apio.ini"

    # -- Error if apio.ini already exists.
    if ini_path.exists():
        cerror("The file apio.ini already exists.")
        sys.exit(1)

    # -- Construct and write the apio.ini file..
    cout(f"Creating {ini_path} file ...")

    section_name = "env:default"

    config = ConfigObj(str(ini_path))
    config.initial_comment = TOP_COMMENT.split("\n")
    config[section_name] = {}
    config[section_name]["board"] = board_id
    config[section_name]["top-module"] = top_module

    config.write()
    cout(f"The file '{ini_path}' was created successfully.", style=SUCCESS)
