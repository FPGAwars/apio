"""The apio context."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

import os
import sys
import json
import platform
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from apio.common.apio_console import cout, cerror, cwarning, cstyle
from apio.common.apio_styles import EMPH3, INFO, EMPH1
from apio.common.common_util import env_build_path
from apio.profile import Profile, RemoteConfigPolicy
from apio.utils import jsonc, util, env_options
from apio.managers.project import Project, load_project_from_file
from apio.utils.resource_util import (
    ProjectResources,
    collect_project_resources,
    validate_project_resources,
    validate_config,
    validate_platforms,
    validate_packages,
)


# ---------- RESOURCES
RESOURCES_DIR = "resources"

# ---------------------------------------
# ---- File: resources/platforms.jsonc
# --------------------------------------
# -- This file contains  the information regarding the supported platforms
# -- and their attributes.
PLATFORMS_JSONC = "platforms.jsonc"

# ---------------------------------------
# ---- File: resources/packages.jsonc
# --------------------------------------
# -- This file contains all the information regarding the available apio
# -- packages: Repository, version, name...
PACKAGES_JSONC = "packages.jsonc"

# -----------------------------------------
# ---- File: resources/boards.jsonc
# -----------------------------------------
# -- Information about all the supported boards
# -- names, fpga family, programmer, ftdi description, vendor id, product id
BOARDS_JSONC = "boards.jsonc"

# -----------------------------------------
# ---- File: resources/fpgas.jsonc
# -----------------------------------------
# -- Information about all the supported fpgas
# -- arch, type, size, packaging
FPGAS_JSONC = "fpgas.jsonc"

# -----------------------------------------
# ---- File: resources/programmers.jsonc
# -----------------------------------------
# -- Information about all the supported programmers
# -- name, command to execute, arguments...
PROGRAMMERS_JSONC = "programmers.jsonc"

# -----------------------------------------
# ---- File: resources/config.jsonc
# -----------------------------------------
# -- General config information.
CONFIG_JSONC = "config.jsonc"


@dataclass(frozen=True)
class EnvMutations:
    """Contains mutations to the system env."""

    # -- PATH items to add.
    paths: List[str]
    # -- Vars name/value paris.
    vars: List[Tuple[str, str]]


class ProjectPolicy(Enum):
    """Represents the possible context policies regarding loading apio.ini.
    and project related information."""

    # -- Project information is not loaded.
    NO_PROJECT = 1
    # -- Project information is loaded if apio.ini is found.
    PROJECT_OPTIONAL = 2
    # -- Apio.ini is required and project information must be loaded.
    PROJECT_REQUIRED = 3


class ApioContext:
    """Apio context. Class for accessing apio resources and configurations."""

    # pylint: disable=too-many-instance-attributes

    # -- List of allowed instance vars.
    __slots__ = (
        "project_policy",
        "home_dir",
        "config",
        "profile",
        "platforms",
        "platform_id",
        "all_packages",
        "platform_packages",
        "boards",
        "fpgas",
        "programmers",
        "env_was_already_set",
        "_project_dir",
        "_project",
        "_project_resources",
    )

    def __init__(
        self,
        *,
        project_policy: ProjectPolicy,
        config_policy: RemoteConfigPolicy,
        project_dir_arg: Optional[Path] = None,
        env_arg: Optional[str] = None,
        report_env=True,
    ):
        """Initializes the ApioContext object.

        'project_policy' controls the loading of the project (apio.ini and
        optional custom resource files.)

        'project_dir_arg' is an optional user specification of the project dir.
        Must be None if project_policy is NO_PROJECT.

        'env_arg' is an optional command line option value that select the
        apio.ini env if the project is loaded. it makes sense only when
        project_policy is PROJECT_REQUIRED (enforced by an assertion).

        If an apio.ini project is loaded, the method prints to the user the
        selected env and board, unless if report_env = False.
        """

        # pylint: disable=too-many-arguments

        # -- Inform as soon as possible about the list of apio env options
        # -- that modify its default behavior.
        defined_env_options = env_options.get_defined()
        if defined_env_options:
            cout(
                f"Active env options [{', '.join(defined_env_options)}].",
                style=INFO,
            )

            if env_options.APIO_HOME_DIR in defined_env_options:
                cwarning(
                    f"Env variable ${env_options.APIO_HOME_DIR} "
                    f"is deprecated, please use ${env_options.APIO_HOME}.",
                )

        # -- Store the project_policy
        assert isinstance(
            project_policy, ProjectPolicy
        ), "Not an ApioContextScope"
        self.project_policy = project_policy

        # -- Sanity check, env_arg makes sense only when project_policy is
        # -- PROJECT_REQUIRED.
        if env_arg is not None:
            assert project_policy == ProjectPolicy.PROJECT_REQUIRED

        # -- A flag to indicate if the system env was already set in this
        # -- apio session. Used to avoid multiple repeated settings that
        # -- make the path longer and longer.
        self.env_was_already_set = False

        # -- Determine if we need to load the project, and if so, set
        # -- self._project_dir to the project dir, otherwise, leave it None.
        self._project_dir: Path = None
        if project_policy == ProjectPolicy.PROJECT_REQUIRED:
            self._project_dir = util.user_directory_or_cwd(
                project_dir_arg, description="Project", must_exist=True
            )
        elif project_policy == ProjectPolicy.PROJECT_OPTIONAL:
            project_dir = util.user_directory_or_cwd(
                project_dir_arg, description="Project", must_exist=False
            )
            if (project_dir / "apio.ini").exists():
                self._project_dir = project_dir
        else:
            assert (
                project_policy == ProjectPolicy.NO_PROJECT
            ), f"Unexpected project policy: {project_policy}"
            assert (
                project_dir_arg is None
            ), "project_dir_arg specified for project policy None"

        # -- Determine apio home dir.
        self.home_dir: Path = util.resolve_home_dir()

        # -- Read and validate the config information
        self.config = self._load_resource(CONFIG_JSONC)
        validate_config(self.config)

        # -- Profile information, from ~/.apio/profile.json. We provide it with
        # -- the remote config url template from distribution.jsonc such that
        # -- can it fetch the remote config on demand.
        remote_config_url = env_options.get(
            env_options.APIO_REMOTE_CONFIG_URL,
            default=self.config["remote-config-url"],
        )
        remote_config_ttl_days = self.config["remote-config-ttl-days"]
        remote_config_retry_minutes = self.config[
            "remote-config-retry-minutes"
        ]
        self.profile = Profile(
            self.home_dir,
            remote_config_url,
            remote_config_ttl_days,
            remote_config_retry_minutes,
            config_policy,
        )

        # -- Read the platforms information.
        self.platforms = self._load_resource(PLATFORMS_JSONC)
        validate_platforms(self.platforms)

        # -- Determine the platform_id for this APIO session.
        self.platform_id = self._determine_platform_id(self.platforms)

        # -- Read the apio packages information
        self.all_packages = self._load_resource(PACKAGES_JSONC)
        validate_packages(self.all_packages)

        # -- Expand in place the env templates in all_packages.
        ApioContext._resolve_package_envs(self.all_packages, self.packages_dir)

        # The subset of packages that are applicable to this platform.
        self.platform_packages = self._select_packages_for_platform(
            self.all_packages, self.platform_id, self.platforms
        )

        # -- Read the boards information. Allow override files in project dir.
        self.boards = self._load_resource(BOARDS_JSONC, allow_custom=True)

        # -- Read the FPGAs information. Allow override files in project dir.
        self.fpgas = self._load_resource(FPGAS_JSONC, allow_custom=True)

        # -- Read the programmers information. Allow override files in project
        # -- dir.
        self.programmers = self._load_resource(
            PROGRAMMERS_JSONC, allow_custom=True
        )

        # -- If we determined that we need to load the project, load the
        # -- apio.ini data.
        self._project: Optional[Project] = None
        self._project_resources: ProjectResources = None

        if self._project_dir:
            # -- Load the project object
            self._project = load_project_from_file(
                self._project_dir, env_arg, self.boards
            )
            assert self.has_project, "init(): project not loaded"
            # -- Inform the user about the active env, if needed..
            if report_env:
                self.report_env()
            # -- Collect and validate the project resources.
            # -- The project is already validated to have the required "board.
            self._project_resources = collect_project_resources(
                self._project.get_str_option("board"),
                self.boards,
                self.fpgas,
                self.programmers,
            )
            # -- Validate the project resources.
            validate_project_resources(self._project_resources)
        else:
            assert not self.has_project, "init(): project loaded"

    def report_env(self):
        """Report to the user the env and board used. Asserts that the
        project is loaded."""
        # -- Do not call if project is not loaded.
        assert self.has_project

        # -- Env name string in color
        styled_env_name = cstyle(self.project.env_name, style=EMPH1)

        # -- Board id string in color
        styled_board_id = cstyle(
            self.project.env_options["board"], style=EMPH1
        )

        # -- Report.
        cout(f"Using env {styled_env_name} ({styled_board_id})")

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
        """Return the project. Should be called only if has_project() is
        True."""
        # -- Failure here is a programming error, not a user error.
        assert self.has_project, "project(): project is not loaded"
        return self._project

    @property
    def project_resources(self) -> ProjectResources:
        """Return the project resources. Should be called only if
        has_project() is True."""
        # -- Failure here is a programming error, not a user error.
        assert self.has_project, "project(): project is not loaded"
        return self._project_resources

    @property
    def env_build_path(self) -> str:
        """Returns the relative path of the current env build directory from
        the project dir. Should be called only when has_project is True."""
        assert self.has_project, "project(): project is not loaded"
        return env_build_path(self.project.env_name)

    def _load_resource(self, name: str, allow_custom: bool = False) -> dict:
        """Load the resources from a given jsonc file
        * INPUTS:
          * Name: Name of the jsonc file
            Use the following constants:
              * PACKAGES_JSONC
              * BOARD_JSONC
              * FPGAS_JSONC
              * PROGRAMMERS_JSONC
              * CONFIG_JSONC
            * Allow_custom: if true, look first in the project dir for
              a project specific resource file of same name.
        * OUTPUT: A dictionary with the jsonc file data
          In case of error it raises an exception and finish
        """
        # -- Try loading a custom resource file from the project directory.
        # -- Since this method is called in an early stage of __init__(), we
        # -- can't use the abstracted self.project_dir.
        if self._project_dir:
            filepath = self._project_dir / name
            if filepath.exists():
                if allow_custom:
                    cout(f"Loading custom '{name}'.")
                    return self._load_resource_file(filepath)

        # -- Load the stock resource file from the APIO package.
        filepath = util.get_path_in_apio_package(RESOURCES_DIR) / name
        return self._load_resource_file(filepath)

    @staticmethod
    def _load_resource_file(filepath: Path) -> dict:
        """Load the resources from a given jsonc file path
        * OUTPUT: A dictionary with the jsonc file data
          In case of error it raises an exception and finish
        """

        # -- Read the jsonc file
        try:
            with filepath.open(encoding="utf8") as file:

                # -- Read the json with comments file
                data_jsonc = file.read()

        # -- The jsonc file NOT FOUND! This is an apio system error
        # -- It should never occur unless there is a bug in the
        # -- apio system files, or a bug when calling this function
        # -- passing a wrong file
        except FileNotFoundError as exc:

            # -- Display error information
            cerror("[Internal] .jsonc file not found", f"{exc}")

            # -- Abort!
            sys.exit(1)

        # -- Convert the jsonc to json by removing '//' comments.
        data_json = jsonc.to_json(data_jsonc)

        # -- Parse the json format!
        try:
            resource = json.loads(data_json)

        # -- Invalid json format! This is an apio system error
        # -- It should never occur unless a developer has
        # -- made a mistake when changing the jsonc file
        except json.decoder.JSONDecodeError as exc:

            # -- Display Main error
            cerror("Invalid .jsonc file", f"{exc}")
            cout(f"File: {filepath}", style=INFO)

            # -- Abort!
            sys.exit(1)

        # -- Return the object for the resource
        return resource

    @staticmethod
    def _expand_env_template(template: str, package_path: Path) -> str:
        """Fills a packages env value template as they appear in
        packages.jsonc. Currently it recognizes only a single place holder
        '%p' representing the package absolute path. The '%p" can appear only
        at the beginning of the template.

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
        The information is a JSON dict originated at packages.json().
        Exits with an error message if the package is not defined.
        """
        package_info = self.platform_packages.get(package_name, None)
        if package_info is None:
            cerror(f"Unknown package '{package_name}'")
            sys.exit(1)

        return package_info

    def get_package_dir(self, package_name: str) -> Path:
        """Returns the root path of a package with given name."""

        return self.packages_dir / package_name

    def get_tmp_dir(self, create: bool = True) -> Path:
        """Return the tmp dir under the apio home dir. If 'create' is true
        create the dir and its parents if they do not exist."""
        tmp_dir = self.home_dir / "tmp"
        if create:
            tmp_dir.mkdir(parents=True, exist_ok=True)
        return tmp_dir

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

        # Stick to the naming conventions we use for boards, fpgas, etc.
        platform_id = platform_id.replace("_", "-")

        # -- Verify it's valid. This can be a user error if the override
        # -- is invalid.
        if platform_id not in platforms.keys():
            cerror(f"Unknown platform id: [{platform_id}]")
            cout(
                "For the list of supported platforms "
                "type 'apio system platforms'.",
                style=INFO,
            )
            sys.exit(1)

        # -- All done ok.
        return platform_id

    @staticmethod
    def _select_packages_for_platform(
        all_packages: Dict[str, Dict],
        platform_id: str,
        platforms: Dict[str, Dict],
    ) -> Dict:
        """Given a dictionary with the packages.jsonc packages infos,
        returns subset dictionary with packages that are available for
        'platform_id'.
        """

        # -- If fails, this is a programming error.
        assert platform_id in platforms, platform

        # -- Final dict with the output packages
        filtered_packages = {}

        # -- Check all the packages
        for package_name in all_packages.keys():

            # -- Get the package info.
            package_info = all_packages[package_name]

            # -- Get the list of platforms ids on which this package is
            # -- available. The package is available on all platforms unless
            # -- restricted by the ""restricted-to-platforms" field.
            available_on_platforms = package_info.get(
                "restricted-to-platforms", platforms.keys()
            )

            # -- Sanity check that all platform ids are valid. If fails it's
            # -- a programming error.
            for p in available_on_platforms:
                assert p in platforms.keys(), platform

            # -- If available for 'platform_id', add it.
            if platform_id in available_on_platforms:
                filtered_packages[package_name] = all_packages[package_name]

        # -- Return the subset dict with the packages for 'platform_id'.
        return filtered_packages

    @staticmethod
    def _get_system_platform_id() -> str:
        """Return a String with the current platform:
        ex. linux-x86-64
        ex. windows-amd64"""

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

    @property
    def is_linux(self) -> bool:
        """Returns True iff platform_id indicates linux."""
        return "linux" in self.platform_id

    @property
    def is_darwin(self) -> bool:
        """Returns True iff platform_id indicates Mac OSX."""
        return "darwin" in self.platform_id

    @property
    def is_windows(self) -> bool:
        """Returns True iff platform_id indicates windows."""
        return "windows" in self.platform_id

    def _get_env_mutations_for_packages(self) -> EnvMutations:
        """Collects the env mutation for each of the defined packages,
        in the order they are defined."""

        result = EnvMutations([], [])
        for _, package_config in self.platform_packages.items():
            # -- Get the json 'env' section. We require it, even if it's empty,
            # -- for clarity reasons.
            assert "env" in package_config
            package_env = package_config["env"]

            # -- Collect the path values.
            path_list = package_env.get("path", [])
            result.paths.extend(path_list)

            # -- Collect the env vars (name, value) pairs.
            vars_section = package_env.get("vars", {})
            for var_name, var_value in vars_section.items():
                result.vars.append((var_name, var_value))

        return result

    def _dump_env_mutations(self, mutations: EnvMutations) -> None:
        """Dumps a user friendly representation of the env mutations."""
        cout("Environment settings:", style=EMPH3)

        # -- Print PATH mutations.
        windows = self.is_windows
        for p in reversed(mutations.paths):
            styled_name = cstyle("PATH", style=EMPH3)
            if windows:
                cout(f"set {styled_name}={p};%PATH%")
            else:
                cout(f'{styled_name}="{p}:$PATH"')

        # -- Print vars mutations.
        for name, val in mutations.vars:
            styled_name = cstyle(name, style=EMPH3)
            if windows:
                cout(f"set {styled_name}={val}")
            else:
                cout(f'{styled_name}="{val}"')

    def _apply_env_mutations(self, mutations: EnvMutations) -> None:
        """Apply a given set of env mutations, while preserving their order."""

        # -- Apply the path mutations, while preserving order.
        old_val = os.environ["PATH"]
        items = mutations.paths + [old_val]
        new_val = os.pathsep.join(items)
        os.environ["PATH"] = new_val

        # -- Apply the vars mutations, while preserving order.
        for name, value in mutations.vars:
            os.environ[name] = value

    def set_env_for_packages(
        self, *, quiet: bool = False, verbose: bool = False
    ) -> None:
        """Sets the environment variables for using all the that are
        available for this platform, even if currently not installed.

        The function sets the environment only on first call and in latter
        calls skips the operation silently.

        If quite is set, no output is printed. When verbose is set, additional
        output such as the env vars mutations are printed, otherwise, a minimal
        information is printed to make the user aware that they commands they
        see are executed in a modified env settings.
        """

        # -- If this fails, this is a programming error. Quiet and verbose
        # -- cannot be combined.
        assert not (quiet and verbose), "Can't have both quite and verbose."

        # -- Collect the env mutations for all packages.
        mutations = self._get_env_mutations_for_packages()

        if verbose:
            self._dump_env_mutations(mutations)

        # -- If this is the first call in this apio invocation, apply the
        # -- mutations. These mutations are temporary for the lifetime of this
        # -- process and does not affect the user's shell environment.
        # -- The mutations are also inherited by child processes such as the
        # -- scons processes.
        if not self.env_was_already_set:
            self._apply_env_mutations(mutations)
            self.env_was_already_set = True
            if not verbose and not quiet:
                cout("Setting shell vars.")
