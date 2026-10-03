"""The apio context."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

import os

from enum import Enum, unique
from pathlib import Path
import json5
from apio.common import subprocess_env, apio_platforms
from apio.common.apio_console import cout, cstyle, fatal_error
from apio.common.apio_styles import INFO, EMPH1
from apio.common.common_util import env_build_path
from apio.common.proto.stubs.apio_common_pb2 import EnvMutations
from apio.managers.profile import Profile
from apio.managers.remote_config import RemoteConfig, RemoteConfigPolicy
from apio.utils import util, env_options
from apio.common.proto.stubs.apio_resources_pb2 import (
    ApioConfig,
    ApioPackageSpec,
)
from apio.common.apio_platforms import ApioPlatform
from apio.managers.project import Project, load_project_from_file
from apio.managers.package_manager import PackageManager
from apio.managers.apio_definitions import (
    ApioDefinitions,
    ProjectDefinitions,
    collect_project_definitions,
)
from apio.utils.resource_util import (
    read_apio_config_file,
    read_apio_packages_file,
)


@unique
class ProjectPolicy(Enum):
    """Represents the possible context policies regarding loading apio.ini.
    and project related information."""

    # -- Project information is not loaded.
    NO_PROJECT = 1
    # -- Project information is loaded if apio.ini is found.
    PROJECT_OPTIONAL = 2
    # -- Apio.ini is required and project information must be loaded.
    PROJECT_REQUIRED = 3


@unique
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
        "all_packages",
        "required_packages",
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
        project_dir_arg: Path | None = None,
        env_arg: str | None = None,
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

        # -- Read and validate the config information
        self.config: ApioConfig = read_apio_config_file()

        # -- Read the user profile from ~/.apio/profile.json.
        self.profile = Profile(
            self.apio_home_dir,
        )

        # -- Read remote config information, from local cache or remotely..
        remote_config_url = env_options.get(
            env_options.APIO_REMOTE_CONFIG_URL,
            default=self.config.remote_config_url,
        )
        assert isinstance(remote_config_url, str), remote_config_url

        self.remote_config = RemoteConfig(
            self.apio_home_dir,
            remote_config_url,
            self.config.remote_config_ttl_days,
            self.config.remote_config_retry_minutes,
            remote_config_policy,
        )

        # -- Get the underlying platform information.
        self.platform: ApioPlatform = apio_platforms.get_apio_platform()

        # -- Read the apio packages information. This method also expands the
        # -- env path placeholders.
        self.all_packages: dict[str, ApioPackageSpec] = (
            read_apio_packages_file(self.apio_packages_dir)
        )

        # -- The subset of packages that are applicable to this platform.
        self.required_packages: dict[str, ApioPackageSpec] = (
            self._select_required_packages_for_platform(
                self.all_packages,
                self.platform.id,
            )
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
        self._project: Project | None = None
        self._project_resources: ProjectDefinitions | None = None

        if self._project_dir:
            # -- If we have a project, we must also have definitions.
            assert self.definitions is not None

            # -- Load the project object
            self._project = load_project_from_file(
                self._project_dir, env_arg, self.definitions.boards
            )
            assert self.has_project, "init(): project not loaded"
            # -- Inform the user about the active env, if needed..
            if report_env:
                self.report_project_env()
            # -- Collect and validate the project resources.
            # -- The project is already validated to have the required "board.
            self._project_resources = collect_project_definitions(
                self._project.get_str_option("board"),
                self.definitions,
            )
        else:
            assert not self.has_project, "init(): project loaded"

    def report_project_env(self):
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
        assert self._project is not None
        return self._project

    @property
    def project_resources(self) -> ProjectDefinitions:
        """Return the project resources. Should be called only if
        has_project() is True."""
        # -- Failure here is a programming error, not a user error.
        assert self.has_project, "project(): project is not loaded"
        assert self._project_resources is not None
        return self._project_resources

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

            fatal_error(
                f"Failed to read and parse resource file {name}", cause=e
            )

        # -- Return the object for the resource
        return json_dict

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
    def _select_required_packages_for_platform(
        all_packages: dict[str, ApioPackageSpec],
        platform_id: str,
    ) -> dict[str, ApioPackageSpec]:
        """Given a dictionary with the apio packages spec, return the subset
        that is used by the given platform_id.
        """

        # -- Dict of all supported platforms.
        all_platform_ids = apio_platforms.get_apio_platforms().keys()

        # -- If fails, this is a programming error.
        assert platform_id in all_platform_ids, platform_id

        # -- Collect the packages that are required for platform_id
        result: dict[str, ApioPackageSpec] = {}
        for package_name, package_spec in all_packages.items():
            # -- Get the list of platforms ids on which this package is
            # -- available. The package is available on all platforms unless
            # -- restricted by the "restricted-to-platforms" field.
            package_platforms: list[str] = list(
                package_spec.restricted_to_platforms
            )
            if len(package_platforms) == 0:
                package_platforms.extend(all_platform_ids)

            # -- Sanity check that all platform ids are valid. If fails it's
            # -- a programming error.
            for p in package_platforms:
                assert p in all_platform_ids, p

            # -- Select the package if it matches the platform.
            if platform_id in package_platforms:
                result[package_name] = package_spec

        # -- All done
        return result

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

    def get_env_mutations_for_subprocess(
        self, *, include_apio_packages: bool
    ) -> EnvMutations:
        """Get the environment mutations for the tools that apio runs in
        a sub process.
        """

        self.required_packages = (
            self.required_packages if include_apio_packages else {}
        )

        return subprocess_env.get_env_mutations_for_subprocess(
            self.platform,
            util.is_pyinstaller_app(),
            self.required_packages,
        )

    def get_env_for_subprocess(
        self,
        *,
        include_apio_packages: bool,
        quiet: bool = False,
        verbose: bool = False,
    ) -> dict[str, str]:
        """Return the env to pass to tools subprocesses such as Yosys.

        If quite is set, no output is printed. When verbose is set, additional
        output such as the env vars mutations are printed, otherwise, a minimal
        information is printed to make the user aware that they commands they
        see are executed in a modified env settings.
        """

        # -- If this fails, this is a programming error. Quiet and verbose
        # -- cannot be combined.
        assert not (quiet and verbose), "Can't have both quite and verbose."

        # -- Collect the env mutations from all packages.
        mutations = self.get_env_mutations_for_subprocess(
            include_apio_packages=include_apio_packages
        )

        if verbose:
            subprocess_env.show_env_mutations(mutations, self.platform)

        # -- Make an independent copy of os.environ.
        env: dict[str, str] = os.environ.copy()

        # -- Apply the mutations to the copy.
        if not verbose and not quiet:
            cout("Setting shell vars.")

        subprocess_env.apply_env_mutations(mutations, env)

        # -- All done.
        return env

    def scons_shell_id(self) -> str:
        """
        Returns a simplified string name of the shell that SCons will use
        for executing shell-dependent commands. See code below for possible
        values.
        """
        return subprocess_env.scons_shell_id(self.platform)
