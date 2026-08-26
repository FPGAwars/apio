"""The apio context."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

import os
import sys
import platform
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict
import json5
from apio.common.apio_console import cout, cerror, cstyle
from apio.common.apio_styles import INFO, EMPH1, EMPH2, EMPH3
from apio.common.common_util import env_build_path
from apio.managers.profile import Profile
from apio.managers.remote_config import RemoteConfig, RemoteConfigPolicy
from apio.utils import util, env_options, apio_platforms
from apio.utils.apio_platforms import ApioPlatform
from apio.managers.project import Project, load_project_from_file
from apio.managers.package_manager import PackageManager
from apio.managers.apio_definitions import ApioDefinitions
from apio.utils.resource_util import (
    ProjectResources,
    collect_project_resources,
    # validate_project_resources,
    validate_config,
    validate_packages,
)

# ---------- RESOURCES
RESOURCES_DIR = "resources"


# ---------------------------------------
# ---- File: resources/packages.jsonc
# --------------------------------------
# -- This file contains all the information regarding the available apio
# -- packages: Repository, version, name...
PACKAGES_JSONC = "packages.jsonc"


# -----------------------------------------
# ---- File: resources/config.jsonc
# -----------------------------------------
# -- General config information.
CONFIG_JSONC = "config.jsonc"


@dataclass(frozen=True)
class EnvMutations:
    """Contains mutations to the system env."""

    # -- List of env vars to unset.
    unset_vars: List[str]

    # -- PATH items to add.
    paths: List[str]

    # -- Dict with env vars name/value to set.
    set_vars: Dict[str, str]


class ProjectPolicy(Enum):
    """Represents the possible context policies regarding loading apio.ini.
    and project related information."""

    # -- Project information is not loaded.
    NO_PROJECT = 1
    # -- Project information is loaded if apio.ini is found.
    PROJECT_OPTIONAL = 2
    # -- Apio.ini is required and project information must be loaded.
    PROJECT_REQUIRED = 3


class PackagesPolicy(Enum):
    """Represents the possible context policies regarding loading apio.ini.
    and project related information."""

    # -- Do not change the package state, they may exist or not, updated or
    # -- not. This policy requires project policy NO_PROJECT and with it,
    # -- the definitions are not loaded.
    IGNORE_PACKAGES = 1
    # -- Normal policy, verify that the packages are installed correctly and
    # -- update them if needed.
    ENSURE_PACKAGES = 2


class ApioContext:
    """Apio context. Class for accessing apio resources and configurations."""

    # pylint: disable=too-many-instance-attributes

    # -- List of allowed instance vars.
    __slots__ = (
        "project_policy",
        "apio_home_dir",
        "apio_packages_dir",
        "config",
        "profile",
        "remote_config",
        "package_manager",
        "platform",
        "platform_id",
        "scons_shell_id",
        "all_packages",
        "required_packages",
        "env_was_already_set",
        "_project_dir",
        "_project",
        "_project_resources",
        "definitions",
    )

    def __init__(
        self,
        *,
        project_policy: ProjectPolicy,
        remote_config_policy: RemoteConfigPolicy,
        packages_policy: PackagesPolicy,
        project_dir_arg: Optional[Path] = None,
        env_arg: Optional[str] = None,
        report_env=True,
    ):
        """Initializes the ApioContext object.

        'project_policy', 'config_policy', and 'packages_policy' are modifiers
        that controls the initialization of the context.

        'project_dir_arg' is an optional user specification of the project dir.
        Must be None if project_policy is NO_PROJECT.

        'env_arg' is an optional command line option value that select the
        apio.ini env if the project is loaded. it makes sense only when
        project_policy is PROJECT_REQUIRED (enforced by an assertion).

        If an apio.ini project is loaded, the method prints to the user the
        selected env and board, unless if report_env = False.
        """

        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-statements

        # -- Sanity check the policies.
        assert isinstance(project_policy, ProjectPolicy)
        assert isinstance(remote_config_policy, RemoteConfigPolicy)
        assert isinstance(packages_policy, PackagesPolicy)

        if packages_policy == PackagesPolicy.IGNORE_PACKAGES:
            assert project_policy == ProjectPolicy.NO_PROJECT

        # -- Inform as soon as possible about the list of apio env options
        # -- that modify its default behavior.
        defined_env_options = env_options.get_defined()
        if defined_env_options:
            cout(
                f"Active env options [{', '.join(defined_env_options)}].",
                style=INFO,
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
        self._project_dir: Path | None = None
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

        # -- Determine apio home and packages dirs
        self.apio_home_dir: Path = util.resolve_home_dir()
        self.apio_packages_dir: Path = util.resolve_packages_dir(
            self.apio_home_dir
        )

        # -- Get the jsonc source dirs.
        resources_dir = util.get_path_in_apio_package(RESOURCES_DIR)

        # -- Read and validate the config information
        self.config = self._load_resource_file(CONFIG_JSONC, resources_dir)
        validate_config(self.config)

        # -- Read the user profile from ~/.apio/profile.json.
        self.profile = Profile(
            self.apio_home_dir,
        )

        # -- Read remote config information, from local cache or remotely..
        remote_config_url = env_options.get(
            env_options.APIO_REMOTE_CONFIG_URL,
            default=self.config["remote-config-url"],
        )
        remote_config_ttl_days = self.config["remote-config-ttl-days"]
        remote_config_retry_minutes = self.config[
            "remote-config-retry-minutes"
        ]

        self.remote_config = RemoteConfig(
            self.apio_home_dir,
            str(remote_config_url),
            remote_config_ttl_days,
            remote_config_retry_minutes,
            remote_config_policy,
        )

        # -- Get the underlying platform information.
        self.platform: ApioPlatform = apio_platforms.get_apio_platform()
        self.platform_id: str = self.platform.id

        # -- Determine the shell id that scons will use.
        # -- See _determine_scons_shell_id() for possible values.
        self.scons_shell_id = self._determine_scons_shell_id(self.platform)

        # -- Read the apio packages information
        self.all_packages = self._load_resource_file(
            PACKAGES_JSONC, resources_dir
        )
        validate_packages(self.all_packages)

        # -- Expand in place the env templates in all_packages.
        ApioContext._resolve_package_envs(
            self.all_packages, self.apio_packages_dir
        )

        # -- The subset of packages that are applicable to this platform.
        self.required_packages = self._select_required_packages_for_platform(
            self.all_packages,
            self.platform_id,
        )

        # -- Instantiate the package manager. All self.* args were already
        # -- initialized above.
        self.package_manager: PackageManager = PackageManager(
            remote_config=self.remote_config,
            required_packages=self.required_packages,
            platform=self.platform,
            apio_home_dir=self.apio_home_dir,
            packages_dir=self.apio_packages_dir,
        )

        # -- Apply package policy

        # -- Case 1: IGNORE_PACKAGES
        if packages_policy == PackagesPolicy.IGNORE_PACKAGES:
            self.definitions = None

        # -- Case 2: ENSURE_PACKAGES
        else:
            assert packages_policy == PackagesPolicy.ENSURE_PACKAGES

            # -- Install missing packages. At this point, the fields that are
            # -- required by self.package_manager are already initialized.
            # --
            # -- TODO: Set verbose=True if APIO_DEBUG is above some level.
            self.package_manager.install_missing_packages_on_the_fly(
                verbose=False
            )

            # -- Load the boards, fpgas, and programmer definitions, including
            # -- optional custom overrides in project's dir.
            self.definitions = ApioDefinitions(
                self.get_package_dir("definitions"),
                self._project_dir,
            )

        # -- If we determined that we need to load the project, load the
        # -- apio.ini data.
        self._project: Optional[Project] = None
        self._project_resources: ProjectResources | None = None

        if self._project_dir:
            # -- Load the project object
            self._project = load_project_from_file(
                self._project_dir, env_arg, self.definitions.boards
            )
            assert self.has_project, "init(): project not loaded"
            # -- Inform the user about the active env, if needed..
            if report_env:
                self.report_env()
            # -- Collect and validate the project resources.
            # -- The project is already validated to have the required "board.
            self._project_resources = collect_project_resources(
                self._project.get_str_option("board"),
                self.definitions,
            )
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
            self.project.get_str_option("board"), style=EMPH1
        )

        # -- Report.
        cout(f"Using env {styled_env_name} ({styled_board_id})")

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
        return self._project  # pyright: ignore[reportReturnType]

    @property
    def project_resources(self) -> ProjectResources:
        """Return the project resources. Should be called only if
        has_project() is True."""
        # -- Failure here is a programming error, not a user error.
        assert self.has_project, "project(): project is not loaded"
        return self._project_resources  # pyright: ignore[reportReturnType]

    @property
    def env_build_path(self) -> Path:
        """Returns the relative path of the current env build directory from
        the project dir. Should be called only when has_project is True."""
        assert self.has_project, "project(): project is not loaded"
        return env_build_path(self.project.env_name)

    @classmethod
    def _load_resource_file(cls, name: str, resources_dir: Path) -> dict:
        """Load a .jsonc resource file and return its content as a
        json dict."""

        # pylint: disable=broad-exception-caught

        # -- Construct file path.
        filepath = resources_dir / name

        # -- Read the and parse the jsonc file
        try:
            jsonc_text = filepath.read_text(encoding="utf-8")
            json_dict = json5.loads(jsonc_text)
        except Exception as e:
            cerror(
                f"Failed to read and parse resource file {name}",
                f"{e}",
            )
            sys.exit(1)

        # -- Return the object for the resource
        return json_dict

    @staticmethod
    def _expand_env_values(template: str, package_path: Path) -> str:
        """Fills a packages env value template as they appear in
        packages.jsonc. Currently it recognizes only a single place holder
        '%p' representing the package absolute path. The '%p" can appear only
        at the beginning of the template.

        E.g. '%p/bin' -> '/users/user/.apio/packages/drivers/bin'

        NOTE: This format is very basic but is sufficient for the current
        needs. If needed, extend or modify it.
        """

        # Case 1: No place holder -> no change.
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
        packages_: Dict[str, Dict], packages_dir: Path
    ) -> None:
        """Resolve in-place the path and var value templates in the
        given packages dictionary. For example, %p is replaced with
        the package's absolute path."""

        for package_name, package_config in packages_.items():

            # -- Get the package root dir.
            package_path = packages_dir / package_name

            # -- Get the json 'env' section. We require it, even if empty,
            # -- for clarity reasons.
            assert "env" in package_config
            package_env = package_config["env"]

            # -- NOTE: There is no need to expand values in the "unset-env"
            # -- section since it contains env names only.

            # -- Expand the values in the "add-to-path" section, if any.
            add_to_path_section = package_env.get("add-to-path", [])
            for i, path_template in enumerate(add_to_path_section):
                add_to_path_section[i] = ApioContext._expand_env_values(
                    path_template, package_path
                )

            # -- Expand the values in the "add-env-vars" section, if any.
            add_env_vars_section = package_env.get("add-env-vars", {})
            for var_name, var_value in add_env_vars_section.items():
                add_env_vars_section[var_name] = (
                    ApioContext._expand_env_values(var_value, package_path)
                )

            # -- Expand the values in the "define-consts" section, if any.
            define_consts_section = package_env.get("define-consts", {})
            for const_name, const_value in define_consts_section.items():
                define_consts_section[const_name] = (
                    ApioContext._expand_env_values(const_value, package_path)
                )

    def get_package_dir(self, package_name: str) -> Path:
        """Returns the root path of a package with given name."""

        return self.apio_packages_dir / package_name

    def get_tmp_dir(self, create: bool = True) -> Path:
        """Return the tmp dir under the apio home dir. If 'create' is true
        create the dir and its parents if they do not exist."""
        tmp_dir = self.apio_home_dir / "tmp"
        if create:
            tmp_dir.mkdir(parents=True, exist_ok=True)
        return tmp_dir

    @staticmethod
    def _determine_scons_shell_id(apio_platform: ApioPlatform) -> str:
        """
        Returns a simplified string name of the shell that SCons will use
        for executing shell-dependent commands. See code below for possible
        values.
        """

        # pylint: disable=too-many-return-statements

        # -- Handle windows.
        if apio_platform.is_windows:
            comspec = os.environ.get("COMSPEC", "").lower()
            if "powershell.exe" in comspec or "pwsh.exe" in comspec:
                return "powershell"
            if "cmd.exe" in comspec:
                return "cmd"
            return "unknown"

        # -- Handle the rest (macOS, Linux, etc.)
        shell_path = os.environ.get("SHELL", "").lower()
        if "bash" in shell_path:
            return "bash"
        if "zsh" in shell_path:
            return "zsh"
        if "fish" in shell_path:
            return "fish"
        if "dash" in shell_path:
            return "dash"
        if "ksh" in shell_path:
            return "ksh"
        if "csh" in shell_path or "tcsh" in shell_path:
            return "cshell"
        return "unknown"

    @staticmethod
    def _select_required_packages_for_platform(
        all_packages: Dict[str, Dict],
        platform_id: str,
    ) -> Dict:
        """Given a dictionary with the packages.jsonc packages infos,
        returns subset dictionary with packages that are available for
        'platform_id'.
        """

        # -- Dict of all supported platforms.
        all_apio_platforms = apio_platforms.get_all_apio_platforms()

        # -- If fails, this is a programming error.
        assert platform_id in all_apio_platforms, platform

        # -- Final dict with the output packages
        filtered_packages = {}

        # -- Check all the packages
        for package_name in all_packages.keys():

            # -- Get the package info.
            package_info = all_packages[package_name]

            # -- Get the list of platforms ids on which this package is
            # -- available. The package is available on all platforms unless
            # -- restricted by the ""restricted-to-platforms" field.
            required_for_platforms = package_info.get(
                "restricted-to-platforms", all_apio_platforms.keys()
            )

            # -- Sanity check that all platform ids are valid. If fails it's
            # -- a programming error.
            for p in required_for_platforms:
                assert p in all_apio_platforms.keys(), platform

            # -- If available for 'platform_id', add it.
            if platform_id in required_for_platforms:
                filtered_packages[package_name] = all_packages[package_name]

        # -- Return the subset dict with the packages for 'platform_id'.
        return filtered_packages

    @property
    def is_linux(self) -> bool:
        """Returns True iff underlying platform is a Linux."""
        return self.platform.is_linux

    @property
    def is_darwin(self) -> bool:
        """Returns True iff underlying platform is a Mac OSX."""
        return self.platform.is_darwin

    @property
    def is_windows(self) -> bool:
        """Returns True iff underlying platform is a Windows."""
        return self.platform.is_windows

    def _get_env_mutations_for_packages(self) -> EnvMutations:
        """Collects the env mutation for each of the defined packages,
        in the order they are defined."""

        unset_vars: List[str] = []
        paths: List[str] = []
        set_vars: Dict[str, str] = {}
        for _, package_config in self.required_packages.items():
            # -- Get the json 'env' section. We require it, even if it's empty,
            # -- for clarity reasons.
            assert "env" in package_config
            package_env = package_config["env"]

            # -- Collect the env vars to delete.
            delete_env_vars_section = package_env.get("delete-env-vars", [])
            for var_name in delete_env_vars_section:
                # -- Detect duplicates.
                assert var_name not in unset_vars, var_name
                unset_vars.append(var_name)

            # -- Collect the path values.
            package_paths = package_env.get("add-to-path", [])
            paths.extend(package_paths)

            # -- Collect the env vars to add (name, value) pairs.
            add_env_vars_section = package_env.get("add-env-vars", {})
            for var_name, var_value in add_env_vars_section.items():
                # -- Detect duplicates.
                assert var_name not in set_vars, var_name
                set_vars[var_name] = var_value

        return EnvMutations(unset_vars, paths, set_vars)

    def _dump_env_mutations(self, mutations: EnvMutations) -> None:
        """Dumps a user friendly representation of the env mutations."""
        cout("Environment settings:", style=EMPH2)

        # -- Print PATH mutations.
        windows = self.is_windows

        # -- Print unset vars.
        for name in mutations.unset_vars:
            styled_name = cstyle(name, style=EMPH3)
            if windows:
                cout(f"  set {styled_name}=")
            else:
                cout(f"  unset {styled_name}")

        # -- Dump paths.
        for p in reversed(mutations.paths):
            styled_name = cstyle("PATH", style=EMPH3)
            if windows:
                cout(f"  set {styled_name}={p};%PATH%")
            else:
                cout(f'  {styled_name}="{p}:$PATH"')

        # -- Print set vars.
        for name, val in mutations.set_vars.items():
            styled_name = cstyle(name, style=EMPH3)
            if windows:
                cout(f"  set {styled_name}={val}")
            else:
                cout(f'  {styled_name}="{val}"')

    def _apply_env_mutations(self, mutations: EnvMutations) -> None:
        """Apply a given set of env mutations, while preserving their order."""

        # -- Apply the unset var mutations
        for name in mutations.unset_vars:
            os.environ.pop(name, None)

        # -- Apply the path mutations, while preserving order.
        # -- NOTE: We treat the old path items as a single items.
        old_val = os.environ["PATH"]
        items = mutations.paths + [old_val]
        new_val = os.pathsep.join(items)
        os.environ["PATH"] = new_val

        # -- Apply the set var mutations
        for name, value in mutations.set_vars.items():
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
