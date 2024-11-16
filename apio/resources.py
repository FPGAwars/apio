"""Resources module"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import sys
import json
import platform
from collections import OrderedDict
import shutil
from pathlib import Path
from typing import Optional, Dict
import click
from apio import util
from apio.profile import Profile


# pylint: disable=fixme
# TODO: Rename this file and class to repreent its more general role and the
# main apio data holder. For example ApioContext or ApioEnv.

# -- Info message
BOARDS_MSG = (
    "\nUse `apio create --board <boardname>` to create a new apio "
    "project for that board\n"
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


# pylint: disable=too-many-instance-attributes
class Resources:
    """Resource manager. Class for accesing to all the resources."""

    def __init__(
        self,
        *,
        project_scope: bool,
        platform_id_override: str = "",
        project_dir: Optional[Path] = None,
    ):
        """Initializes the Resources object. 'project dir' is an optional path
        to the project dir, otherwise, the current directory is used.
        'project_scope' indicates if project specfic resources such as
        boards.json should be loaded, if available' or that the global
        default resources should be used instead.  Some commands such as
        'apio packages' uses the global scope while commands such as
        'apio build' use the project scope.
        """
        # -- Maps the optional project_dir option to a path.
        self.project_dir: Path = util.get_project_dir(project_dir)

        # -- Profile information, from ~/.apio/profile.json
        self.profile = Profile()

        # -- Read the platforms information.
        self.platforms = self._load_resource(PLATFORMS_JSON)

        # -- Determine the platform_id for this APIO session.
        self.platform_id = self._determine_platform_id(
            platform_id_override, self.platforms
        )

        # -- Read the apio packages information
        self.all_packages = self._load_resource(PACKAGES_JSON)

        # -- Expand in place the env templates in all_packages.
        Resources._resolve_package_envs(self.all_packages)

        # The subset of packages that are applicable to this platform.
        self.platform_packages = self._select_packages_for_platform(
            self.all_packages, self.platform_id, self.platforms
        )

        # -- Read the boards information
        self.boards = self._load_resource(
            BOARDS_JSON, allow_custom=project_scope
        )

        # -- Read the FPGAs information
        self.fpgas = self._load_resource(
            FPGAS_JSON, allow_custom=project_scope
        )

        # -- Read the programmers information
        self.programmers = self._load_resource(
            PROGRAMMERS_JSON, allow_custom=project_scope
        )

        # -- Read the distribution information
        self.distribution = self._load_resource(DISTRIBUTION_JSON)

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
        filepath = self.project_dir / name

        if filepath.exists():
            if allow_custom:
                click.secho(f"Loading project's custom '{name}' file.")
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

                # -- Read the json file
                data_json = file.read()

        # -- json file NOT FOUND! This is an apio system error
        # -- It should never ocurr unless there is a bug in the
        # -- apio system files, or a bug when calling this function
        # -- passing a wrong file
        except FileNotFoundError as exc:

            # -- Display Main error
            click.secho("Apio System Error! JSON file not found", fg="red")

            # -- Display the affected file (in a different color)
            apio_file_msg = click.style("Apio file: ", fg="yellow")
            filename = click.style(f"{filepath}", fg="blue")
            click.secho(f"{apio_file_msg} {filename}")

            # -- Display the specific error message
            click.secho(f"{exc}\n", fg="red")

            # -- Abort!
            sys.exit(2)

        # -- Parse the json format!
        try:
            resource = json.loads(data_json)

        # -- Invalid json format! This is an apio system error
        # -- It should never ocurr unless some develeper has
        # -- made a mistake when changing the json file
        except json.decoder.JSONDecodeError as exc:

            # -- Display Main error
            click.secho("Apio System Error! Invalid JSON file", fg="red")

            # -- Display the affected file (in a different color)
            apio_file_msg = click.style("Apio file: ", fg="yellow")
            filename = click.style(f"{filepath}", fg="blue")
            click.secho(f"{apio_file_msg} {filename}")

            # -- Display the specific error message
            click.secho(f"{exc}\n", fg="red")

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
    def _resolve_package_envs(packages: Dict[str, Dict]) -> None:
        """Resolve in place the path and var value templates in the
        given packages dictionary. For example, %p is replaced with
        the package's absolute path."""

        packages_dir = util.get_packages_dir()
        for _, package_config in packages.items():

            # -- Get the package root dir.
            package_path = (
                packages_dir / package_config["release"]["folder_name"]
            )

            # -- Get the json 'env' section. We require it, even if empty,
            # -- for clarity reasons.
            assert "env" in package_config
            package_env = package_config["env"]

            # -- Expand the values in the "path" section, if any.
            path_section = package_env.get("path", [])
            for i, path_template in enumerate(path_section):
                path_section[i] = Resources._expand_env_template(
                    path_template, package_path
                )

            # -- Expand the values in the "vars" section, if any.
            vars_section = package_env.get("vars", {})
            for var_name, val_template in vars_section.items():
                vars_section[var_name] = Resources._expand_env_template(
                    val_template, package_path
                )

    def get_package_folder_name(self, package_name: str) -> str:
        """Returns name of the package folder, within the packages dir."""

        try:
            package_folder_name = self.platform_packages[package_name][
                "release"
            ]["folder_name"]

        # -- This error should never ocurr
        except KeyError as excp:
            click.secho(f"Apio System Error! Invalid key: {excp}", fg="red")
            click.secho(
                "Module: resources.py. Function: get_package_release_name()",
                fg="red",
            )

            # -- Abort!
            sys.exit(1)

        except TypeError as excp:

            click.secho(f"Apio System Error! {excp}", fg="red")
            click.secho(
                "Module: resources.py. Function: get_package_release_name()",
                fg="red",
            )

            # -- Abort!
            sys.exit(1)

        # -- Return the name
        return package_folder_name

    def get_platform_packages_lists(self) -> tuple[list, list]:
        """Get all the packages that are applicable to this platform,
        grouped as installed and not installed
        * OUTPUT:
          - A tuple of two lists: Installed and not installed packages
        """

        # -- Classify the packages in two lists
        installed_packages = []
        notinstalled_packages = []

        # -- Go though all the apio packages and add them to the installed
        # -- or uninstalled lists.
        for package_name, package_config in self.platform_packages.items():

            # -- Collect information about the package
            data = {
                "name": package_name,
                "version": None,
                "description": package_config["description"],
            }

            # -- Check if this package is installed
            if package_name in self.profile.packages:

                # -- Get the installed version
                version = self.profile.packages[package_name]["version"]

                # -- Store the version
                data["version"] = version

                # -- Store the package
                installed_packages += [data]

            # -- The package is not installed
            else:
                notinstalled_packages += [data]

        # -- If there are in the profile packages that are not in the
        # -- platform packages, add them well to the uninstalled list, as
        # -- 'unknown'. These must be some left overs, e.g. if apio is
        # -- upgraded.
        for package_name in self.profile.packages:
            if package_name not in self.platform_packages:
                data = {
                    "name": package_name,
                    "version": "Unknown",
                    "description": "Unknown deprecated package",
                }
                installed_packages += [data]

        # -- Return the packages, classified
        return installed_packages, notinstalled_packages

    def list_packages(self, installed=True, notinstalled=True):
        """Return a list with all the installed/notinstalled packages"""

        # Classify packages
        installed_packages, notinstalled_packages = (
            self.get_platform_packages_lists()
        )

        # -- Calculate the terminal width
        terminal_width, _ = shutil.get_terminal_size()

        # -- String with a horizontal line with the same width
        # -- as the terminal
        line = "─" * terminal_width
        dline = "═" * terminal_width

        if installed and installed_packages:

            # ------- Print installed packages table
            # -- Print the header
            click.secho()
            click.secho(dline, fg="green")
            click.secho("Installed packages:", fg="green")

            for package in installed_packages:
                click.secho(line)
                name = click.style(f"{package['name']}", fg="cyan", bold=True)
                version = package["version"]
                description = package["description"]

                click.secho(f"• {name} {version}")
                click.secho(f"  {description}")

            click.secho(dline, fg="green")
            click.secho(f"Total: {len(installed_packages)}")

        if notinstalled and notinstalled_packages:

            # ------ Print not installed packages table
            # -- Print the header
            click.secho()
            click.secho(dline, fg="yellow")
            click.secho("Available packages (Not installed):", fg="yellow")

            for package in notinstalled_packages:

                click.secho(line)
                name = click.style(f"• {package['name']}", fg="red")
                description = package["description"]
                click.secho(f"{name}  {description}")

            click.secho(dline, fg="yellow")
            click.secho(f"Total: {len(notinstalled_packages)}")

        click.secho("\n")

    def get_package_dir(self, package_name: str) -> Path:
        """Returns the root path of a package with given name."""

        package_folder = self.get_package_folder_name(package_name)
        package_dir = util.get_packages_dir() / package_folder

        return package_dir

    # R0914: Too many local variables (17/15)
    # pylint: disable=R0914
    def list_boards(self):
        """Print all the supported boards and the information of
        their FPGAs
        """
        # Get terminal configuration. It will help us to adapt the format
        # to a terminal vs a pipe.
        config: util.TerminalConfig = util.get_terminal_config()

        # -- Table title
        title = (
            click.style("Board", fg="cyan") + " (FPGA, Arch, Type, Size, Pack)"
        )

        # -- Print the table header for terminal mode.
        if config.terminal_mode():
            title = (
                click.style("Board", fg="cyan")
                + " (FPGA, Arch, Type, Size, Pack)"
            )
            # -- Horizontal line across the terminal.
            seperator_line = "─" * config.terminal_width
            click.secho(seperator_line)
            click.secho(title)
            click.secho(seperator_line)

        # -- Sort boards names by case insentive alphabetical order.
        board_names = list(self.boards.keys())
        board_names.sort(key=lambda x: x.lower())

        # -- For a pipe, determine the max example name length.
        max_board_name_len = max(len(x) for x in board_names)

        # -- Print all the boards!
        for board in board_names:

            # -- Generate the report for a terminal. Color and multi lines
            # -- are ok.

            # -- Get board FPGA long name
            fpga = self.boards[board]["fpga"]

            # -- Get information about the FPGA
            arch = self.fpgas[fpga]["arch"]
            type_ = self.fpgas[fpga]["type"]
            size = self.fpgas[fpga]["size"]
            pack = self.fpgas[fpga]["pack"]

            # -- Print the item with information
            # -- Print the Board in a differnt color

            item_fpga = f"(FPGA:{fpga}, {arch}, {type_}, {size}, {pack})"

            if config.terminal_mode():
                # -- Board name with a bullet point and color
                board_str = click.style(board, fg="cyan")
                item_board = f"• {board_str}"

                # -- Item in one line
                one_line_item = f"{item_board}  {item_fpga}"

                # -- If there is enough space, print in one line
                if len(one_line_item) <= config.terminal_width:
                    click.secho(one_line_item)

                # -- Not enough space: Print it in two separate lines
                else:
                    two_lines_item = f"{item_board}\n      {item_fpga}"
                    click.secho(two_lines_item)

            else:
                # -- Generate the report for a pipe. Single line, no color, no
                # -- bullet points.
                click.secho(f"{board:<{max_board_name_len}} |  {item_fpga}")

        if config.terminal_mode():
            # -- Print the Footer
            click.secho(seperator_line)
            click.secho(f"Total: {len(self.boards)} boards")

            # -- Help message
            click.secho(BOARDS_MSG, fg="green")

    def list_fpgas(self):
        """Print all the supported FPGAs"""

        # Get terminal configuration. It will help us to adapt the format
        # to a terminal vs a pipe.
        config: util.TerminalConfig = util.get_terminal_config()

        if config.terminal_mode():
            # -- Horizontal line across the terminal,
            seperator_line = "─" * config.terminal_width

            # -- Table title
            fpga_header = click.style(f"{'  FPGA':34}", fg="cyan")
            title = (
                f"{fpga_header} {'Arch':<10} {'Type':<13}"
                f" {'Size':<8} {'Pack'}"
            )

            # -- Print the table header
            click.secho(seperator_line)
            click.secho(title)
            click.secho(seperator_line)

        # -- Print all the fpgas!
        for fpga in self.fpgas:

            # -- Get information about the FPGA
            arch = self.fpgas[fpga]["arch"]
            _type = self.fpgas[fpga]["type"]
            size = self.fpgas[fpga]["size"]
            pack = self.fpgas[fpga]["pack"]

            # -- Print the item with information
            data_str = f"{arch:<10} {_type:<13} {size:<8} {pack}"
            if config.terminal_mode():
                # -- For terminal, print the FPGA name in color.
                fpga_str = click.style(f"{fpga:32}", fg="cyan")
                item = f"• {fpga_str} {data_str}"
                click.secho(item)
            else:
                # -- For pipe, no colors and no bullet point.
                click.secho(f"{fpga:32} {data_str}")

        # -- Print the Footer
        if config.terminal_mode():
            click.secho(seperator_line)
            click.secho(f"Total: {len(self.fpgas)} fpgas\n")

    @staticmethod
    def _determine_platform_id(
        platform_id_override: str, platforms: Dict[str, Dict]
    ) -> str:
        """Determines and returns the platform io based on system info and
        optional override."""
        # -- Use override and get from the underlying system.
        if platform_id_override:
            platform_id = platform_id_override
        else:
            platform_id = Resources._get_system_platform_id()

        # -- Verify it's valid. This can be a user error if the override
        # -- is invalid.
        if platform_id not in platforms.keys():
            click.secho(f"Error: unknown platform id: [{platform_id}]")
            click.secho(
                "\n"
                "[Hint]: For the list of supported platforms\n"
                "type 'apio system --platforms'.",
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
