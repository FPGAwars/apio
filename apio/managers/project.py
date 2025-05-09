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
from abc import ABC, abstractmethod
import re
import configparser
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Optional, Union, Any, List, Tuple
from configobj import ConfigObj
from apio.utils import util
from apio.common.apio_console import cout, cerror, cwarning
from apio.common.apio_styles import INFO, SUCCESS


DEFAULT_TOP_MODULE = "main"

ENV_NAME_REGEX = re.compile(r"^[a-z][a-z0-9-]*$")

ENV_NAME_HINT = (
    "Env names should start with a-z, "
    "followed by any number of a-z, 0-9, and '-'."
)

TOP_COMMENT = """\
APIO project configuration file. For details see
https://github.com/FPGAwars/apio/wiki/Project-configuration-file
"""

# -- Apio options. These are the options that appear in the [apio] section.
# -- They are not subject to inheritance and resolution.

# -- The options docs here are formatted in the rich-text format of the
# -- python rich library. See apio_info.py to see how they are
# -- used.
APIO_DEFAULT_ENV_DOC = """
The option 'default-env' selects the default env to use if --env is not \
specified on the command line. Without it, the first env in apio.ini is \
used as the default. This option is useful when apio.ini has more than one \
env.

Example:[code]
  [apio]
  default-env = bar

  [env:foo]
  ...

  [env:bar]
  ...[/code]
"""

APIO_OPTIONS = {
    # -- Selecting the env to use if not overridden in command line. Otherwise
    # -- the first env is the default.
    "default-env": APIO_DEFAULT_ENV_DOC,
}


# -- Env options. These are options that appear in the [common] and [env:*]
# -- sections of apio.ini. The 'require' attribute refers to their apperance
# -- in the env options after resolving the inheritance.

# -- The options docs here are formatted in the rich-text format of the
# -- python rich library. See apio_info.py to see how they are
# -- used.
ENV_BOARD_OPTION_DOC = """
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

ENV_TOP_MODULE_OPTION_DOC = """
The option 'top-module' specifies the name of the top module of the design. \
If 'top-module' is not specified, Apio assumes the default name 'main'; \
however, it is a good practice to always explicitly specify the top module.

Example:[code]
  top-module = my_main[/code]
"""

ENV_DEFAULT_TESTBENCH_DOC = """
The option 'default-testbench' is useful in projects that have more than \
a single testbench file, because it allows specifying the default testbench \
that will be simulated when the command 'apio sim' is run without a testbench \
argument.

Without this option, Apio will exit with an error message if the project \
contains more than one testbench file and a testbench was not specified in \
the 'apio sim' command.

Example:[code]
  default-testbench = my_module_tb.v
  default-testbench = my_module_tb.sv[/code]
"""

ENV_FORMAT_VERIBLE_OPTIONS_DOC = """
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

ENV_YOSYS_SYNTH_EXTRA_OPTIONS_DOC = """
The option 'yosys-synth-extra-options' allows adding options to the \
yosys synth command. In the example below, it adds the option '-dsp', \
which enables for some FPGAs the use of DSP cells to implement multiply \
operations. This is an advanced and esoteric option that is typically \
not needed.

Example:[code]
  yosys-synth-extra-options = -dsp[/code]
"""

ENV_OPTIONS = {
    # -- The board name.
    "board": ENV_BOARD_OPTION_DOC,
    # -- The top module name. Default is 'main'.
    "top-module": ENV_TOP_MODULE_OPTION_DOC,
    # -- The default testbench name for 'apio sim'.
    "default-testbench": ENV_DEFAULT_TESTBENCH_DOC,
    # -- Multi line list of verible options for 'apio format'
    "format-verible-options": ENV_FORMAT_VERIBLE_OPTIONS_DOC,
    # -- Additional option for the yosys synth command (inside the -p arg).
    "yosys-synth-extra-options": ENV_YOSYS_SYNTH_EXTRA_OPTIONS_DOC,
}

# -- The subset of the options in OPTIONS that are required.
ENV_REQUIRED_OPTIONS = {
    "board",
}


class ProjectResolver(ABC):
    """An abstract class with services that are needed for project validation.
    Generally speaking it provides a subset of the functionality of ApioContext
    and we use it to avoid a cyclic import between Project and ApioContext.
    """

    # pylint: disable=too-few-public-methods

    @abstractmethod
    def lookup_board_name(self, board: str) -> str:
        """Similar to ApioContext.lookup_board()"""


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
        resolver: ProjectResolver,
    ):
        """Construct a Project object with given options sections and a
        resolver with context information."""

        if util.is_debug():
            print(f"Parsed [apio] section:\n  {apio_section}")
            print(f"Parsed [common] section:\n  {common_section}")
            print(f"Parsed [env:*] sections:\n  {env_sections}")

        # -- Validate the sections.
        Project.validate_sections(
            apio_section=apio_section,
            common_section=common_section,
            env_sections=env_sections,
            resolver=resolver,
        )

        # -- Determine active env name and options.
        self._env_name = Project.resolve_default_env_name(
            apio_section, env_sections
        )
        self._env_options = Project.resolve_env_options(
            self._env_name, common_section, env_sections
        )
        if util.is_debug():
            print(f"Resolved env name: {self._env_name}")
            print(f"Resolved env options: {self._env_options}")

        # TODO: Debug code. Remove.
        # print()
        # print(f"Parsed [apio] section: {apio_section}")
        # print(f"Parsed [common] section: {common_section}")
        # print(f"Parsed [env:*] sections: {env_sections}")
        # print(f"Resolved env name: {self._env_name}")
        # print(f"Resolved env options: {self._env_options}")
        # print()

        # -- Validate the resolved env. This is where we check for required
        # -- options.
        Project.validate_resolved_env(
            self._env_name, self._env_options, resolver
        )

    @staticmethod
    def validate_apio_ini_env_name(env_name: str):
        """Validate the given env name. Use only for env names found in
        apio.ini, not from command lines or other sources."""
        if not ENV_NAME_REGEX.match(env_name):
            cerror(f"Invalid apio env name '{env_name}' in apio.ini.")
            cout(ENV_NAME_HINT, style=INFO)
            sys.exit(1)

    @staticmethod
    def validate_sections(
        apio_section: Optional[Dict[str, str]],
        common_section: Optional[Dict[str, str]],
        env_sections: Dict[str, Dict[str, str]],
        resolver: ProjectResolver,
    ):
        """Validate the parsed apio.ini sections."""

        # -- Validate the apio section.
        Project.validate_apio_section(apio_section, env_sections)

        # -- Validate the common section.
        Project.validate_env_section("[common]", common_section, resolver)

        # -- Validate the env sections.
        for env_name, section_options in env_sections.items():
            Project.validate_apio_ini_env_name(env_name)
            Project.validate_env_section(
                f"[env:{env_name}]", section_options, resolver
            )

    @staticmethod
    def validate_apio_section(
        apio_section: Dict[str, str], env_sections: Dict[str, Dict[str, str]]
    ):
        """Validate the [apio] section."""

        # -- Look for unknown options.
        for option in apio_section:
            if option not in APIO_OPTIONS:
                cerror(
                    f"Unknown option '{option} in [apio] section of apio.ini'"
                )
                sys.exit(1)

        # -- If 'board' option exists, verify the board exists.
        default_env_name = apio_section.get("default-env", None)
        if default_env_name:
            Project.validate_apio_ini_env_name(default_env_name)
            if default_env_name not in env_sections:
                cerror(f"Env '{default_env_name}' not found in apio.ini.")
                cout(
                    f"Expecting an env section '{default_env_name}' "
                    "in apio.ini",
                    style=INFO,
                )
                sys.exit(1)

    @staticmethod
    def validate_env_section(
        section_title: str, section_options: Dict[str, str], resolver
    ):
        """Validate the options of a section that contains env options. This
        includes the sections [env:*] and [common]."""

        # -- Check that there are no unknown options.
        for option in section_options:
            if option not in ENV_OPTIONS:
                cerror(
                    f"Unknown option '{option}' in {section_title} "
                    "section of apio.ini."
                )
                sys.exit(1)

        # -- If 'board' option exists, verify the board exists.
        if "board" in section_options:
            # -- This exits with an error if board does not exist.
            resolver.lookup_board_name(section_options["board"])

    @staticmethod
    def resolve_default_env_name(
        apio_section: Dict[str, str], env_sections: Dict[str, Dict[str, str]]
    ) -> str:
        """Determines the active env name. Sections are assumed to be
        validated."""
        # -- Priority #1 (highest): The optional default-env option in the
        # -- [apio] section.
        env_name = apio_section.get("default-env", None)

        # -- Priority #2 (lowest): Picking the first env defined in apio.ini.
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
    def resolve_env_options(
        env_name,
        common_section: Dict[str, str],
        env_sections: Dict[str, Dict[str, str]],
    ) -> Tuple[str, Dict[str, str]]:
        """Returns env name and options. Sections are prevalidated"""

        # -- Get the options of selected env.
        env_section: Dict[str, str] = env_sections[env_name]

        # -- Merge the options while preserving their order in apio.ini.
        env_options = {}
        # -- Add common options that are not in env section
        for name, val in common_section.items():
            if name not in env_section:
                env_options[name] = val
        # -- Add all the options from the env section.
        for name, val in env_section.items():
            env_options[name] = val

        # -- All done.
        return env_options

    @staticmethod
    def validate_resolved_env(
        env_name: str, env_options: Dict[str, str], resolver: ProjectResolver
    ):
        """Validate the resolved env options. These are the option after
        selecting the active env and resolving the options inheritance."""

        # -- Check that all the required options are present.
        for option in ENV_REQUIRED_OPTIONS:
            if option not in env_options:
                cerror(
                    f"Missing option '{option}' "
                    f"after resolving env {env_name}."
                )
                sys.exit(1)

        # -- We already validated the sections for unknown options so don't
        # -- need to check here.

        # -- Force 'board' to have the canonical name of the board.
        # -- This exists with an error message if the board is unknown.
        env_options["board"] = resolver.lookup_board_name(env_options["board"])

        # -- If top-module was not specified, fill in the default value.
        if "top-module" not in env_options:
            env_options["top-module"] = DEFAULT_TOP_MODULE
            cout(
                "Option 'top-module' is missing, "
                f"using '{DEFAULT_TOP_MODULE}'.",
                style=INFO,
            )

    def get(self, option: str, default: Any = None) -> Union[str, Any]:
        """Lookup an env option value by name. Returns default if not found."""
        # -- If this fails, this is a programming error.
        assert option in ENV_OPTIONS, f"Invalid env option: [{option}]"

        # -- Lookup with default
        return self._env_options.get(option, default)

    def __getitem__(self, option: str) -> Optional[str]:
        """Lookup an env option value by name using the [] operator. Returns
        None if not found."""
        return self.get(option, None)

    def get_as_lines_list(
        self, option: str, default: Any = None
    ) -> Union[List[str], Any]:
        """Lookup an env option value that has a line list format. Returns
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
        resolver=resolver,
    )


def create_project_file(
    project_dir: Path,
    board_name: str,
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

    config = ConfigObj(str(ini_path))
    config.initial_comment = TOP_COMMENT.split("\n")
    config["env"] = {}
    config["env"]["board"] = board_name
    config["env"]["top-module"] = top_module

    config.write()
    cout(f"The file '{ini_path}' was created successfully.", style=SUCCESS)
