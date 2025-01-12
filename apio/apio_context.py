"""The apio context."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import sys
import json
import platform
from enum import Enum
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Dict
import click
from click import secho
from apio import util, env_options
from apio.profile import Profile
from apio import jsonc
from apio.managers.project import (
    Project,
    ProjectResolver,
    load_project_from_file,
    APIO_INI,
)


# ---------- RESOURCES
RESOURCES_DIR = "resources"

# ---------------------------------------
# ---- File: resources/platforms.json
# --------------------------------------
# -- This file contains  the information regarding the supported platforms
# -- and their attributes.
PLATFORMS_JSON = "platforms.json"

# ---------------------------------------
# ---- File: resources/packages.json
# --------------------------------------
# -- This file contains all the information regarding the available apio
# -- packages: Repository, version, name...
PACKAGES_JSON = "packages.json"

# -----------------------------------------
# ---- File: resources/boads.json
# -----------------------------------------
# -- Information about all the supported boards
# -- names, fpga family, programmer, ftdi description, vendor id, product id
BOARDS_JSON = "boards.json"

# -----------------------------------------
# ---- File: resources/fpgas.json
# -----------------------------------------
# -- Information about all the supported fpgas
# -- arch, type, size, packaging
FPGAS_JSON = "fpgas.json"

# -----------------------------------------
# ---- File: resources/programmers.json
# -----------------------------------------
# -- Information about all the supported programmers
# -- name, command to execute, arguments...
PROGRAMMERS_JSON = "programmers.json"

# -----------------------------------------
# ---- File: resources/distribution.json
# -----------------------------------------
# -- Information about all the supported apio and pip packages
DISTRIBUTION_JSON = "distribution.json"


class ApioContextScope(Enum):
    """Represents the possible scopes of ApioContext creations."""

    # -- Apio.ini and optional custom resource files are not loaded.
    NO_PROJECT = 1
    # -- If project dir contains a file named apio.ini then the project
    # -- and optional custom resources are loaded.
    PROJECT_OPTIONAL = 2
    # -- Project dir must contain the apio.ini file and it is always loaded
    # -- together with optional custom resource files.
    PROJECT_REQUIRED = 3


# pylint: disable=too-many-instance-attributes
class ApioContext:
    """Apio context. Class for accesing apio resources and configurations."""

    def __init__(
        self,
        *,
        scope: ApioContextScope,
        project_dir_arg: Optional[Path] = None,
    ):
        """Initializes the ApioContext object.

        'scope' controls the loading of the project (apio.ini and
        optional custom resource files.)

        'project_dir_arg' is an optional user specification of the project dir.
        Must be None if scope is NO_PROJECT.

        """

        # -- Set color on/off based on the option profile.json.
        Profile.apply_color_preferences()

        # -- Inform as soon as possible about the list of apio env options
        # -- that modify its default behavior.
        defined_env_options = env_options.get_defined()
        if defined_env_options:
            secho(
                f"Active env options [{', '.join(defined_env_options)}].",
                fg="yellow",
            )

        # -- Store the scope
        assert isinstance(scope, ApioContextScope), "Not an ApioContextScope"
        self.scope = scope

        # -- A flag to indicate if the system env was already set in this
        # -- apio session. Used to avoid multiple repeated settings that
        # -- make the path longer and longer.
        self.env_was_already_set = False

        # -- Determine if we need to load the project, and if so, set
        # -- self._project_dir to the project dir, otherwise, leave it None.
        self._project_dir: Path = None
        if scope == ApioContextScope.PROJECT_REQUIRED:
            self._project_dir = util.resolve_project_dir(
                project_dir_arg, must_exist=True
            )
        elif scope == ApioContextScope.PROJECT_OPTIONAL:
            project_dir = util.resolve_project_dir(project_dir_arg)
            if (project_dir / APIO_INI).exists():
                self._project_dir = project_dir
        else:
            assert (
                scope == ApioContextScope.NO_PROJECT
            ), f"Unexpected scope: {scope}"
            assert (
                project_dir_arg is None
            ), "project_dir_arg specified for scope None"

        # -- Determine apio home dir.
        self.home_dir: Path = util.resolve_home_dir()

        # -- Read the distribution information
        self.distribution = self._load_resource(DISTRIBUTION_JSON)

        # -- Profile information, from ~/.apio/profile.json. We provide it with
        # -- the remote config url template from disribution.json such that
        # -- can it fetch the remote config on demand.
        self.profile = Profile(
            self.home_dir, self.distribution["remote-config"]
        )

        # -- Read the platforms information.
        self.platforms = self._load_resource(PLATFORMS_JSON)

        # -- Determine the platform_id for this APIO session.
        self.platform_id = self._determine_platform_id(self.platforms)

        # -- Read the apio packages information
        self.all_packages = self._load_resource(PACKAGES_JSON)

        # -- Expand in place the env templates in all_packages.
        ApioContext._resolve_package_envs(self.all_packages, self.packages_dir)

        # The subset of packages that are applicable to this platform.
        self.platform_packages = self._select_packages_for_platform(
            self.all_packages, self.platform_id, self.platforms
        )

        # -- Read the boards information. Allow override files in project dir.
        self.boards = self._load_resource(BOARDS_JSON, allow_custom=True)

        # -- Read the FPGAs information. Allow override files in project dir.
        self.fpgas = self._load_resource(FPGAS_JSON, allow_custom=True)

        # -- Read the programmers information. Allow override files in project
        # -- dir.
        self.programmers = self._load_resource(
            PROGRAMMERS_JSON, allow_custom=True
        )

        # -- Sort resources for consistency and intunitiveness.
        # --
        # -- We don't sort the all_packages and platform_packages dictionaries
        # -- because that will affect the order of the env path items.
        # -- Instead we preserve the order from the packages.json file.

        self.boards = OrderedDict(
            sorted(self.boards.items(), key=lambda t: t[0])
        )
        self.fpgas = OrderedDict(
            sorted(self.fpgas.items(), key=lambda t: t[0])
        )

        # -- If we determined that we need to load the project, load the
        # -- apio.ini data.
        self._project: Optional[Project] = None
        if self._project_dir:
            resolver = _ProjectResolverImpl(self)
            self._project = load_project_from_file(self._project_dir, resolver)
            assert self.has_project, "init(): project not loaded"
        else:
            assert not self.has_project, "init(): project loaded"

    def lookup_board_name(
        self, board: str, *, warn: bool = True, strict: bool = True
    ) -> str:
        """Lookup and return the board's canonical board name which is its key
        in boards.json().  'board' can be the canonical name itself or a
        legacy id of the board as defined in boards.json.  The method prints
        a warning if 'board' is a legacy board name that is mapped to its
        canonical name and 'warn' is True. If the  board is not found, the
        method returns None if 'strict' is False or exit the program with a
        message if 'strict' is True."""
        # -- If this fails, it's a programming error.
        assert board is not None

        # -- The result. The board's key in boards.json.
        canonical_name = None

        if board in self.boards:
            # -- Here when board is already the canonical name.
            canonical_name = board
        else:
            # -- Look up for a board with 'board' as its legacy name.
            for board_name, board_info in self.boards.items():
                if board == board_info.get("legacy_name", None):
                    canonical_name = board_name
                    break

        # -- Fatal error if unknown board.
        if strict and canonical_name is None:
            secho(f"Error: no such board '{board}'", fg="red")
            secho(
                "Run 'apio boards' for the list of board names.\n"
                "Expecting a board name such as 'alhambra-ii'.",
                fg="yellow",
            )
            sys.exit(1)

        # -- Warning if caller used a legacy board name.
        if warn and canonical_name and board != canonical_name:
            secho(
                f"Warning: '{board}' board name was changed. "
                f"Please use '{canonical_name}' instead.",
                fg="yellow",
            )

        # -- Return the canonical board name.
        return canonical_name

    @property
    def packages_dir(self):
        """Returns the directory hat contains the installed apio packages."""
        return self.home_dir / "packages"

    @property
    def has_project(self):
        """Returns True if the project is loaded."""
        return self._project is not None

    @property
    def project_dir(self):
        """Returns the project dir. Should be called only if has_project_loaded
        is true."""
        assert self.has_project, "project_dir(): project is not loaded"
        assert self._project_dir, "project_dir(): missing value."
        return self._project_dir

    @property
    def project(self) -> Project:
        """Return the project. Should be called only if has_project_loaded() is
        True."""
        # -- Failure here is a programming error, not a user error.
        assert self.has_project, "project(): project is not loaded"
        return self._project

    def _load_resource(self, name: str, allow_custom: bool = False) -> dict:
        """Load the resources from a given json file
        * INPUTS:
          * Name: Name of the json file
            Use the following constants:
              * PACKAGES_JSON
              * BOARD_JSON
              * FPGAS_JSON
              * PROGRAMMERS_JSON
              * DISTRIBUTION_JSON
            * Allow_custom: if true, look first in the project dir for
              a project specific resource file of same name.
        * OUTPUT: A dictionary with the json file data
          In case of error it raises an exception and finish
        """
        # -- Try loading a custom resource file from the project directory.
        # -- Since this method is called in an early stage of __init__(), we
        # -- can't use the abstracted self.project_dir.
        if self._project_dir:
            filepath = self._project_dir / name
            if filepath.exists():
                if allow_custom:
                    secho(f"Loading custom '{name}'.")
                    return self._load_resource_file(filepath)

        # -- Load the stock resource file from the APIO package.
        filepath = util.get_path_in_apio_package(RESOURCES_DIR) / name
        return self._load_resource_file(filepath)

    @staticmethod
    def _load_resource_file(filepath: Path) -> dict:
        """Load the resources from a given json file path
        * OUTPUT: A dictionary with the json file data
          In case of error it raises an exception and finish
        """

        # -- Read the json file
        try:
            with filepath.open(encoding="utf8") as file:

                # -- Read the json with comments file
                data_jsonc = file.read()

        # -- json file NOT FOUND! This is an apio system error
        # -- It should never ocurr unless there is a bug in the
        # -- apio system files, or a bug when calling this function
        # -- passing a wrong file
        except FileNotFoundError as exc:

            # -- Display Main error
            secho("Apio System Error! JSON file not found", fg="red")

            # -- Display the affected file (in a different color)
            apio_file_msg = click.style("Apio file: ", fg="yellow")
            filename = click.style(f"{filepath}", fg="cyan", bold=True)
            secho(f"{apio_file_msg} {filename}")

            # -- Display the specific error message
            secho(f"{exc}\n", fg="red")

            # -- Abort!
            sys.exit(1)

        # -- Convert the jsonc to json by removing '//' comments.
        data_json = jsonc.to_json(data_jsonc)

        # -- Parse the json format!
        try:
            resource = json.loads(data_json)

        # -- Invalid json format! This is an apio system error
        # -- It should never ocurr unless some develeper has
        # -- made a mistake when changing the json file
        except json.decoder.JSONDecodeError as exc:

            # -- Display Main error
            secho("Apio System Error! Invalid JSON file", fg="red")

            # -- Display the affected file (in a different color)
            apio_file_msg = click.style("Apio file: ", fg="yellow")
            filename = click.style(f"{filepath}", fg="cyan", bold=True)
            secho(f"{apio_file_msg} {filename}")

            # -- Display the specific error message
            secho(f"{exc}\n", fg="red")

            # -- Abort!
            sys.exit(1)

        # -- Return the object for the resource
        return resource

    @staticmethod
    def _expand_env_template(template: str, package_path: Path) -> str:
        """Fills a packages env value template as they appear in packages.json.
        Currently it recognizes only a single place holder '%p' representing
        the package absolute path. The '%p" can appear only at the begigning
        of the template.

        E.g. '%p/bin' -> '/users/user/.apio/packages/drivers/bin'

        NOTE: This format is very basic but is sufficient for the current
        needs. If needed, extend or modify it.
        """

        # Case 1: No place holder.
        if "%p" not in template:
            return template

        # Case 2: The template contains only the placeholder.
        if template == "%p":
            return str(package_path)

        # Case 3: The place holder is the prefix of the template's path.
        if template.startswith("%p/"):
            return str(package_path / template[3:])

        # Case 4: Unsupported.
        raise RuntimeError(f"Invalid env template: [{template}]")

    @staticmethod
    def _resolve_package_envs(
        packages: Dict[str, Dict], packages_dir: Path
    ) -> None:
        """Resolve in place the path and var value templates in the
        given packages dictionary. For example, %p is replaced with
        the package's absolute path."""

        for package_name, package_config in packages.items():

            # -- Get the package root dir.
            package_path = packages_dir / package_name

            # -- Get the json 'env' section. We require it, even if empty,
            # -- for clarity reasons.
            assert "env" in package_config
            package_env = package_config["env"]

            # -- Expand the values in the "path" section, if any.
            path_section = package_env.get("path", [])
            for i, path_template in enumerate(path_section):
                path_section[i] = ApioContext._expand_env_template(
                    path_template, package_path
                )

            # -- Expand the values in the "vars" section, if any.
            vars_section = package_env.get("vars", {})
            for var_name, val_template in vars_section.items():
                vars_section[var_name] = ApioContext._expand_env_template(
                    val_template, package_path
                )

    def get_package_info(self, package_name: str) -> str:
        """Returns the information of the package with given name.
        The information is a JSON dict originated at packages.jsnon().
        Exits with an error message if the package is not defined.
        """
        package_info = self.platform_packages.get(package_name, None)
        if package_info is None:
            secho(f"Error: unknown package '{package_name}'", fg="red")
            sys.exit(1)

        return package_info

    def get_package_dir(self, package_name: str) -> Path:
        """Returns the root path of a package with given name."""

        return self.packages_dir / package_name

    @staticmethod
    def _determine_platform_id(platforms: Dict[str, Dict]) -> str:
        """Determines and returns the platform io based on system info and
        optional override."""
        # -- Use override and get from the underlying system.
        platform_id_override = env_options.get(env_options.APIO_PLATFORM)
        if platform_id_override:
            platform_id = platform_id_override
        else:
            platform_id = ApioContext._get_system_platform_id()

        # -- Verify it's valid. This can be a user error if the override
        # -- is invalid.
        if platform_id not in platforms.keys():
            secho(f"Error: unknown platform id: [{platform_id}]")
            secho(
                "\n"
                "[Hint]: For the list of supported platforms\n"
                "type 'apio system platforms'.",
                fg="yellow",
            )
            sys.exit(1)

        # -- All done ok.
        return platform_id

    @staticmethod
    def _select_packages_for_platform(
        all_packages: Dict[str, Dict],
        platform_id: str,
        platforms: Dict[str, Dict],
    ):
        """Given a dictionary with the packages.json packages configurations,
        returns subset dictionary with packages that are applicable to the
        this platform.
        """

        # -- Final dict with the output packages
        filtered_packages = {}

        # -- Check all the packages
        for package_name in all_packages.keys():

            # -- Get the information about the package
            release = all_packages[package_name]["release"]

            # -- This packages is available only for certain platforms.
            if "available_platforms" in release:

                # -- Get the available platforms
                available_platforms = release["available_platforms"]

                # -- Check all the available platforms
                for available_platform in available_platforms:

                    # -- Sanity check. If this fails, it's a programming error
                    # -- rather than a user error.
                    assert available_platform in platforms, (
                        f"Unknown available platform: '{available_platform}' "
                        "in package '{pkg}'"
                    )

                    # -- Match!
                    if platform_id == available_platform:

                        # -- Add it to the output dictionary
                        filtered_packages[package_name] = all_packages[
                            package_name
                        ]

            # -- Package for all the platforms
            else:

                # -- Add it to the output dictionary
                filtered_packages[package_name] = all_packages[package_name]

        # -- Update the current packages!
        return filtered_packages

    @staticmethod
    def _get_system_platform_id() -> str:
        """Return a String with the current platform:
        ex. linux_x86_64
        ex. windows_amd64"""

        # -- Get the platform: linux, windows, darwin
        type_ = platform.system().lower()
        platform_str = f"{type_}"

        # -- Get the architecture
        arch = platform.machine().lower()

        # -- Special case for windows
        if type_ == "windows":
            # -- Assume all the windows to be 64-bits
            arch = "amd64"

        # -- Add the architecture, if it exists
        if arch:
            platform_str += f"_{arch}"

        # -- Return the full platform
        return platform_str

    def is_linux(self) -> bool:
        """Returns True iff platform_id indicates linux."""
        return "linux" in self.platform_id

    def is_darwin(self) -> bool:
        """Returns True iff platform_id indicates Mac OSX."""
        return "darwin" in self.platform_id

    def is_windows(self) -> bool:
        """Returns True iff platform_id indicates windows."""
        return "windows" in self.platform_id


# pylint: disable=too-few-public-methods
class _ProjectResolverImpl(ProjectResolver):
    def __init__(self, apio_context: ApioContext):
        """When ApioContext instanciates this object, ApioContext is fully
        constructed, except for the project field."""
        self._apio_context = apio_context

    # @override
    def lookup_board_name(self, board: str) -> str:
        """Implementation of lookup_board_name."""
        return self._apio_context.lookup_board_name(board)
