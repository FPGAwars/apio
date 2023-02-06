"""DOC: TODO"""
# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import os
import re
import sys
import time
import datetime
import shutil
from os.path import isfile
from pathlib import Path

import click

import pkg_resources
import semantic_version

from apio import util
from apio.managers.arguments import process_arguments
from apio.managers.arguments import format_vars
from apio.managers.system import System
from apio.profile import Profile
from apio.resources import Resources


class SCons:
    """Class for managing the scons tools"""

    def __init__(self, project_dir=""):
        """Initialization:
        * project_dir: path where the sources are located
          If not given, the curent working dir is used
        """

        # -- Read the apio profile file
        self.profile = Profile()

        # -- Read the apio resources
        self.resources = Resources()

        # -- Project path is given
        if project_dir is not None:
            # Check if it is a correct folder
            # (or create a new one)
            project_dir = util.check_dir(project_dir)

            # Change to that folder
            os.chdir(project_dir)

    # W0703: Catching too general exception Exception (broad-except)
    # pylint: disable=W0703
    @util.command
    def clean(self, args):
        """DOC: TODO"""

        try:
            __, __, arch = process_arguments(args, self.resources)

        # -- No architecture given: Uses ice40 as default
        except Exception:
            arch = "ice40"

        # --Clean the project: run scons -c (with aditional arguments)
        return self.run("-c", arch=arch, variables=[], packages=[])

    @util.command
    def verify(self, args):
        """Executes scons for verifying"""

        # -- Split the arguments
        __, __, arch = process_arguments(args, self.resources)

        # -- Execute scons!!!
        # -- The packages to check are passed
        return self.run(
            "verify",
            variables=[],
            arch=arch,
            packages=["oss-cad-suite"],
        )

    @util.command
    def lint(self, args):
        """DOC: TODO"""

        __, __, arch = process_arguments(None, self.resources)
        var = format_vars(
            {
                "all": args.get("all"),
                "top": args.get("top"),
                "nowarn": args.get("nowarn"),
                "warn": args.get("warn"),
                "nostyle": args.get("nostyle"),
            }
        )
        return self.run(
            "lint",
            variables=var,
            arch=arch,
            packages=["oss-cad-suite"],
        )

    @util.command
    def sim(self):
        """DOC: TODO"""

        __, __, arch = process_arguments(None, self.resources)
        return self.run(
            "sim",
            variables=[],
            arch=arch,
            packages=["oss-cad-suite", "gtkwave"],
        )

    @util.command
    def build(self, args):
        """Build the circuit"""

        # -- Split the arguments
        var, board, arch = process_arguments(args, self.resources)

        # -- Execute scons!!!
        # -- The packages to check are passed
        return self.run(
            "build",
            variables=var,
            board=board,
            arch=arch,
            packages=["oss-cad-suite"],
        )

    # run(self, command, variables, packages, board=None, arch=None):

    @util.command
    def time(self, args):
        """DOC: TODO"""

        var, board, arch = process_arguments(args, self.resources)
        return self.run(
            "time",
            variables=var,
            board=board,
            arch=arch,
            packages=["oss-cad-suite"],
        )

    # R0913: Too many arguments (6/5)
    # pylint: disable=R0913
    @util.command
    def upload(self, args, serial_port, ftdi_id, sram, flash):
        """Upload the circuit to the board"""

        # -- Split the arguments
        var, board, arch = process_arguments(args, self.resources)

        # -- Get the programmer for that board
        programmer = self.get_programmer(
            board, serial_port, ftdi_id, sram, flash
        )

        var += [f"prog={programmer}"]

        return self.run(
            "upload",
            variables=var,
            packages=["oss-cad-suite"],
            board=board,
            arch=arch,
        )

    # R0913: Too many arguments (6/5)
    # pylint: disable=R0913
    def get_programmer(self, board, ext_serial, ext_ftdi_id, sram, flash):
        """DOC: TODO"""

        programmer = ""

        if board:
            board_data = self.resources.boards.get(board)

            # Check platform
            self.check_platform(board_data)

            # Check pip packages
            self.check_pip_packages(board_data)

            # Serialize programmer command
            programmer = self.serialize_programmer(board_data, sram, flash)

            # Replace USB vendor id
            if "${VID}" in programmer:
                vid = board_data.get("usb").get("vid")
                programmer = programmer.replace("${VID}", vid)

            # Replace USB product id
            if "${PID}" in programmer:
                pid = board_data.get("usb").get("pid")
                programmer = programmer.replace("${PID}", pid)

            # Replace FTDI index
            if "${FTDI_ID}" in programmer:
                self.check_usb(board, board_data)
                ftdi_id = self.get_ftdi_id(board, board_data, ext_ftdi_id)
                programmer = programmer.replace("${FTDI_ID}", ftdi_id)

            # TinyFPGA BX board is not detected in MacOS HighSierra
            if "tinyprog" in board_data and "darwin" in util.get_systype():
                # In this case the serial check is ignored
                return "tinyprog --libusb --program"

            # Replace Serial port
            if "${SERIAL_PORT}" in programmer:
                self.check_usb(board, board_data)
                device = self.get_serial_port(board, board_data, ext_serial)
                programmer = programmer.replace("${SERIAL_PORT}", device)

        return programmer

    @staticmethod
    def check_platform(board_data):
        """DOC: TODO"""

        if "platform" not in board_data:
            return

        platform = board_data.get("platform")
        current_platform = util.get_systype()
        if platform != current_platform:
            # Incorrect platform
            if platform == "linux_armv7l":
                raise ValueError("incorrect platform: RPI2 or RPI3 required")
            raise ValueError(f"incorrect platform {platform}")

    def check_pip_packages(self, board_data):
        """Check if the corresponding pip package with the programmer
        has already been installed. In the case of an apio package
        it is just ignored
        """

        # -- Get the programmer object for the given board
        prog_info = board_data.get("programmer")

        # -- Get the programmer information (from the type)
        # -- Command, arguments, pip package, etc...
        prog_data = self.resources.programmers.get(prog_info.get("type"))

        # -- Get all the pip packages from the distribution
        all_pip_packages = self.resources.distribution.get("pip_packages")

        # -- Get the name of the pip package of the current programmer,
        # -- if any (The programmer maybe in a pip package or an apio package)
        pip_packages = prog_data.get("pip_packages") or []

        # -- Check if pip package was installed
        # -- In case of an apio package it is just ignored
        for pip_pkg in pip_packages:
            try:
                # Check pip_package version
                spec = semantic_version.Spec(all_pip_packages.get(pip_pkg, ""))
                pkg_version = pkg_resources.get_distribution(pip_pkg).version
                version = semantic_version.Version(pkg_version)
                if not spec.match(version):
                    click.secho(
                        f"Error: '{pip_pkg}' "
                        + f"version ({version}) "
                        + f"does not match {spec}",
                        fg="red",
                    )
                    click.secho(
                        "Please run:\n" f"   pip install -U apio[{pip_pkg}]",
                        fg="yellow",
                    )
                    raise ValueError("Incorrect version number")
            except pkg_resources.DistributionNotFound as exc:
                click.secho(f"Error: '{pip_pkg}' is not installed", fg="red")
                click.secho(
                    "Please run:\n" f"   pip install -U apio[{pip_pkg}]",
                    fg="yellow",
                )
                raise ValueError("Package not installed") from exc
            try:
                # Check pip_package itself
                __import__(pip_pkg)
            except Exception as exc:
                # Exit if a package is not working
                python_version = util.get_python_version()
                message = f"'{pip_pkg}' not compatible with "
                message += f"Python {python_version}"
                message += f"\n       {exc}"
                raise ValueError(message) from exc

    def serialize_programmer(self, board_data, sram, flash):
        """DOC: TODO"""

        prog_info = board_data.get("programmer")
        content = self.resources.programmers.get(prog_info.get("type"))

        programmer = content.get("command")

        # dfu-util needs extra args first
        if programmer.startswith("dfu-util"):
            if prog_info.get("extra_args"):
                programmer += f" {prog_info.get('extra_args')}"

            if content.get("args"):
                programmer += f" {content.get('args')}"
        else:
            # Add args
            if content.get("args"):
                programmer += f" {content.get('args')}"

            # Add extra args
            if prog_info.get("extra_args"):
                programmer += f" {prog_info.get('extra_args')}"

        # Enable SRAM programming
        if sram:
            # Only for iceprog programmer
            if programmer.startswith("iceprog"):
                programmer += " -S"

        if flash:
            # Only for ujprog programmer
            if programmer.startswith("ujprog"):
                programmer = programmer.replace("SRAM", "FLASH")

        return programmer

    @staticmethod
    def check_usb(board, board_data):
        """DOC: TODO"""

        if "usb" not in board_data:
            raise AttributeError("Missing board configuration: usb")

        usb_data = board_data.get("usb")
        hwid = f"{usb_data.get('vid')}:{usb_data.get('pid')}"
        found = False
        for usb_device in System().get_usb_devices():
            if usb_device.get("hwid") == hwid:
                found = True
                break

        if not found:
            # Board not connected
            if "tinyprog" in board_data:
                click.secho(
                    "Activate bootloader by pressing the reset button",
                    fg="yellow",
                )
            raise ConnectionError("board " + board + " not connected")

    def get_serial_port(self, board, board_data, ext_serial_port):
        """DOC: TODO"""

        # Search Serial port by USB id
        device = self._check_serial(board, board_data, ext_serial_port)
        if device is None:
            # Board not connected
            raise ConnectionError("board " + board + " not connected")
        return device

    def _check_serial(self, board, board_data, ext_serial_port):
        """DOC: TODO"""

        if "usb" not in board_data:
            raise AttributeError("Missing board configuration: usb")

        usb_data = board_data.get("usb")
        hwid = f"{usb_data.get('vid')}:{usb_data.get('pid')}"

        # Match the discovered serial ports
        serial_ports = util.get_serial_ports()
        if len(serial_ports) == 0:
            # Board not available
            raise AttributeError("board " + board + " not available")
        for serial_port_data in serial_ports:
            port = serial_port_data.get("port")
            if ext_serial_port and ext_serial_port != port:
                # If the --device options is set but it doesn't match
                # the detected port, skip the port.
                continue
            if hwid.lower() in serial_port_data.get("hwid").lower():
                if "tinyprog" in board_data and not self._check_tinyprog(
                    board_data, port
                ):
                    # If the board uses tinyprog use its port detection
                    # to double check the detected port.
                    # If the port is not detected, skip the port.
                    continue
                # If the hwid and the description pattern matches
                # with the detected port return the port.
                return port
        return None

    @staticmethod
    def _check_tinyprog(board_data, port):
        """DOC: TODO"""

        desc_pattern = "^" + board_data.get("tinyprog").get("desc") + "$"
        for tinyprog_meta in util.get_tinyprog_meta():
            tinyprog_port = tinyprog_meta.get("port")
            tinyprog_name = tinyprog_meta.get("boardmeta").get("name")
            if port == tinyprog_port and re.match(desc_pattern, tinyprog_name):
                # If the port is detected and it matches the pattern
                return True
        return False

    def get_ftdi_id(self, board, board_data, ext_ftdi_id):
        """DOC: TODO"""

        # Search device by FTDI id
        ftdi_id = self._check_ftdi(board, board_data, ext_ftdi_id)
        if ftdi_id is None:
            # Board not connected
            raise AttributeError("board " + board + " not connected")
        return ftdi_id

    @staticmethod
    def _check_ftdi(board, board_data, ext_ftdi_id):
        """DOC: TODO"""

        if "ftdi" not in board_data:
            raise AttributeError("Missing board configuration: ftdi")

        desc_pattern = "^" + board_data.get("ftdi").get("desc") + "$"

        # Match the discovered FTDI chips
        ftdi_devices = System().get_ftdi_devices()
        if len(ftdi_devices) == 0:
            # Board not available
            raise AttributeError("board " + board + " not available")
        for ftdi_device in ftdi_devices:
            index = ftdi_device.get("index")
            # ftdi device indices can start at zero
            if ext_ftdi_id is not None and ext_ftdi_id != index:
                # If the --device options is set but it doesn't match
                # with the detected index, skip the port.
                continue
            if re.match(desc_pattern, ftdi_device.get("description")):
                # If matches the description pattern
                # return the index for the FTDI device.
                return index
        return None

    # R0913: Too many arguments (6/5)
    # pylint: disable=R0913
    def run(self, command, variables, packages, board=None, arch=None):
        """Executes scons"""

        # -- Check if in the current project a custom SConstruct file
        # is being used. We fist build the full name (with the full path)
        scon_file = Path(util.get_project_dir()) / "SConstruct"

        # -- If the SConstruct file does NOT exist, we use the one provided by
        # -- apio, which is located in the resources/arch/ folder
        if not isfile(scon_file):
            # -- This is the default SConstruct file
            resources = util.get_full_path("resources")
            default_scons_file = resources / arch / "SConstruct"

            # -- It is passed to scons using the flag -f default_scons_file
            variables += ["-f", f"{default_scons_file}"]

        else:
            # -- We are using our custom SConstruct file
            click.secho("Info: use custom SConstruct file")

        # -- Check the configuration mode
        if self.profile.check_exe_default():
            # Run on `default` config mode

            # -- Check if the necessary packages are installed
            if not util.resolve_packages(
                packages,
                self.profile.packages,
                self.resources.distribution.get("packages"),
            ):
                # Exit if a package is not installed
                raise AttributeError("Package not installed")
        else:
            click.secho("Info: native config mode")

        # -- Execute scons
        return self._execute_scons(command, variables, board)

    # R0914: Too many local variables (19/15)
    # pylint: disable=R0914
    def _execute_scons(self, command, variables, board):
        """Execute the scons builder"""

        terminal_width, _ = shutil.get_terminal_size()
        start_time = time.time()

        if command in ("build", "upload", "time"):
            if board:
                processing_board = board
            else:
                processing_board = "custom board"

            date_time_str = datetime.datetime.now().strftime("%c")
            board_color = click.style(processing_board, fg="cyan", bold=True)
            click.echo(f"[{date_time_str}] Processing {board_color}")
            click.secho("-" * terminal_width, bold=True)

        scons_command = ["scons"] + ["-Q", command] + variables
        cmd = " ".join(util.exec_command(scons_command))
        if self.profile.get_verbose_mode() > 0:
            click.secho(f"Executing: {cmd}")

        # -- Execute the scons builder
        result = util.exec_command(
            scons_command,
            stdout=util.AsyncPipe(self._on_stdout),
            stderr=util.AsyncPipe(self._on_stderr),
        )

        # -- Print result
        exit_code = result.get("returncode")
        is_error = exit_code != 0
        duration = time.time() - start_time
        summary_text = f" Took {duration:.2f} seconds "
        half_line = "=" * int(((terminal_width - len(summary_text) - 10) / 2))
        status = (
            click.style(" ERROR ", fg="red", bold=True)
            if is_error
            else click.style("SUCCESS", fg="green", bold=True)
        )
        click.echo(
            f"{half_line} [{status}]{summary_text}{half_line}",
            err=is_error,
        )

        return exit_code

    @staticmethod
    def _on_stdout(line):
        fgcol = "green" if "is up to date" in line else None
        click.secho(line, fg=fgcol)

    @staticmethod
    def _on_stderr(line):
        if "%|" in line and "100%|" not in line:
            # Remove previous line for tqdm progress bar
            cursor_up = "\033[F"
            erase_line = "\033[K"
            sys.stdout.write(cursor_up + erase_line)
        fgcol = "red" if "error" in line.lower() else "yellow"
        click.secho(line, fg=fgcol)
