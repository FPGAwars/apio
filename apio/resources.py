"""Resources module"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import sys
import json
from collections import OrderedDict
import shutil
import click
from apio import util
from apio.profile import Profile

# -- Info message
BOARDS_MSG = (
    """
Use `apio init --board <boardname>` to create a new apio """
    """project for that board\n"""
)

# ---------- RESOURCES
RESOURCES_DIR = "resources"
# ---------------------------------------
# ---- File: resources/packages.json
# --------------------------------------
# -- This file contains all the information regarding the available apio
# -- packages: Repository, version, name...
# -- This information is access through the Resources.packages method
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


class Resources:
    """Resource manager. Class for accesing to all the resources"""

    def __init__(self, platform: str = ""):

        # -- Read the apio packages information
        self.packages = self._load_resource(PACKAGES_JSON)

        # -- Read the boards information
        self.boards = self._load_resource(BOARDS_JSON)

        # -- Read the FPGAs information
        self.fpgas = self._load_resource(FPGAS_JSON)

        # -- Read the programmers information
        self.programmers = self._load_resource(PROGRAMMERS_JSON)

        # -- Read the distribution information
        self.distribution = self._load_resource(DISTRIBUTION_JSON)

        # -- Filter packages: Store only the packages for
        # -- the given platform
        self._filter_packages(platform)

        # ---------  Sort resources
        self.packages = OrderedDict(
            sorted(self.packages.items(), key=lambda t: t[0])
        )

        self.boards = OrderedDict(
            sorted(self.boards.items(), key=lambda t: t[0])
        )
        self.fpgas = OrderedDict(
            sorted(self.fpgas.items(), key=lambda t: t[0])
        )

        # -- Default profile file
        self.profile = None

    @staticmethod
    def _load_resource(name: str) -> dict:
        """Load the resources from a given json file
        * INPUTS:
          * Name: Name of the json file
            Use the following constants:
              * PACKAGES_JSON
              * BOARD_JSON
              * FPGAS_JSON
              * PROGRAMMERS_JSON
              * DISTRIBUTION_JSON
        * OUTPUT: The dicctionary with the data
          In case of error it raises an exception and finish
        """

        # -- Build the filepath: Ex. resources/fpgas.json
        filepath = util.get_full_path(RESOURCES_DIR) / name

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

    def get_package_release_name(self, package: str) -> str:
        """return the package name"""

        try:
            package_name = self.packages[package]["release"]["package_name"]

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
        return package_name

    def get_packages(self) -> tuple[list, list]:
        """Get all the packages, classified in installed and
        not installed
        * OUTPUT:
          - A tuple of two lists: Installed and not installed packages
        """

        # -- Classify the packages in two lists
        installed_packages = []
        notinstalled_packages = []

        # -- Go though all the apio packages
        for package in self.packages:

            # -- Collect information about the package
            data = {
                "name": package,
                "version": None,
                "description": self.packages[package]["description"],
            }

            # -- Check if this package is installed
            if package in self.profile.packages:

                # -- Get the installed version
                version = self.profile.packages[package]["version"]

                # -- Store the version
                data["version"] = version

                # -- Store the package
                installed_packages += [data]

            # -- The package is not installed
            else:
                notinstalled_packages += [data]

        # -- Check the installed packages and update
        # -- its information
        for package in self.profile.packages:

            # -- The package is not known!
            # -- Strange case
            if package not in self.packages:
                data = {
                    "name": package,
                    "version": "Unknown",
                    "description": "Unknown deprecated package",
                }
                installed_packages += [data]

        # -- Return the packages, classified
        return installed_packages, notinstalled_packages

    def list_packages(self, installed=True, notinstalled=True):
        """Return a list with all the installed/notinstalled packages"""

        self.profile = Profile()

        # Classify packages
        installed_packages, notinstalled_packages = self.get_packages()

        # -- Calculate the terminal width
        terminal_width, _ = shutil.get_terminal_size()

        # -- String with a horizontal line with the same width
        # -- as the terminal
        line = "─" * terminal_width
        dline = "═" * terminal_width

        if installed and installed_packages:

            # ------- Print installed packages table
            # -- Print the header
            click.echo()
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
            click.echo(f"Total: {len(installed_packages)}")

        if notinstalled and notinstalled_packages:

            # ------ Print not installed packages table
            # -- Print the header
            click.echo()
            click.secho(dline, fg="yellow")
            click.secho("Available packages (Not installed):", fg="yellow")

            for package in notinstalled_packages:

                click.echo(line)
                name = click.style(f"• {package['name']}", fg="red")
                description = package["description"]
                click.echo(f"{name}  {description}")

            click.secho(dline, fg="yellow")
            click.echo(f"Total: {len(notinstalled_packages)}")

        click.echo("\n")

    def list_boards(self):
        """Print all the supported boards and the information of
        their FPGAs
        """

        # -- Table title
        title = (
            click.style("Board", fg="cyan") + " (FPGA, Arch, Type, Size, Pack)"
        )

        # -- Get the terminal size (in characteres)
        terminal_width, _ = shutil.get_terminal_size()

        # -- String with a horizontal line with the same width
        # -- as the terminal
        line = "─" * terminal_width

        # -- Print the table header
        click.echo(line)
        click.echo(title)
        click.echo(line)

        # -- Print all the boards!
        for board in self.boards:

            # -- Get board FPGA long name
            fpga = self.boards[board]["fpga"]

            # -- Get information about the FPGA
            arch = self.fpgas[fpga]["arch"]
            _type = self.fpgas[fpga]["type"]
            size = self.fpgas[fpga]["size"]
            pack = self.fpgas[fpga]["pack"]

            # -- Print the item with information
            # -- Print the Board in a differnt color
            board_str = click.style(board, fg="cyan")
            item_board = f"• {board_str}"
            item_fpga = f"  (FPGA:{fpga}, {arch}, {_type}, {size}, {pack})"

            # -- Item in one line
            item = item_board + item_fpga

            # -- If there is enough space, print in one line
            if len(item) <= terminal_width:
                click.echo(item)

            # -- Not enough space: Print it in two separate lines
            else:
                click.echo(f"{item_board}\n    {item_fpga}")

        # -- Print the Footer
        click.echo(line)
        click.echo(f"Total: {len(self.boards)} boards")

        # -- Help message
        click.secho(BOARDS_MSG, fg="green")

    def list_fpgas(self):
        """Print all the supported FPGAs"""

        # -- Table title
        fpga_header = click.style("FPGA", fg="cyan")
        title = (
            f"{fpga_header:40} {'Arch':<8} {'Type':<12}"
            f" {'Size':<5} {'Pack':<10}"
        )
        # -- Get the terminal size (in characteres)
        terminal_width, _ = shutil.get_terminal_size()

        # -- String with a horizontal line with the same width
        # -- as the terminal
        line = "─" * terminal_width

        # -- Print the table header
        click.echo(line)
        click.echo(title)
        click.echo(line)

        # -- Print all the fpgas!
        for fpga in self.fpgas:

            # -- Get information about the FPGA
            arch = self.fpgas[fpga]["arch"]
            _type = self.fpgas[fpga]["type"]
            size = self.fpgas[fpga]["size"]
            pack = self.fpgas[fpga]["pack"]

            # -- Print the item with information
            # -- Print the FPGA in a differnt color
            fpga_str = click.style(fpga, fg="cyan")
            item = (
                f"• {fpga_str:40} {arch:<8} {_type:<12} {size:<5} {pack:<10}"
            )
            click.echo(item)

        # -- Print the Footer
        click.echo(line)
        click.echo(f"Total: {len(self.fpgas)} fpgas\n")

    def _filter_packages(self, given_platform):
        """Filter the apio packages available for the given platform.
        Some platforms has special packages (Ex. package Drivers is
        only for windows)
        * INPUT:
          * packages: All the apio packages
          * given_platform: Platform used for filtering the packages.
              If not given,the current system platform is used

        self.packages is updated. It now contains only the packages
          for the given platform
        """

        # -- Final dict with the output packages
        filtered_packages = {}

        # -- If not given platform, use the current
        if not given_platform:
            given_platform = util.get_systype()

        # -- Check all the packages
        for pkg in self.packages.keys():

            # -- Get the information about the package
            release = self.packages[pkg]["release"]

            # -- This packages is available only for certain platforms
            if "available_platforms" in release:

                # -- Get the available platforms
                platforms = release["available_platforms"]

                # -- Check all the available platforms
                for platform in platforms:

                    # -- Match!
                    if given_platform in platform:

                        # -- Add it to the output dictionary
                        filtered_packages[pkg] = self.packages[pkg]

            # -- Package for all the platforms
            else:

                # -- Add it to the output dictionary
                filtered_packages[pkg] = self.packages[pkg]

        # -- Update the current packages!
        self.packages = filtered_packages
