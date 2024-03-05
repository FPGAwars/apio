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
from pathlib import Path

import importlib.metadata
import click
import semantic_version

from apio import util
from apio.managers.arguments import process_arguments
from apio.managers.arguments import serialize_scons_flags
from apio.managers.system import System
from apio.profile import Profile
from apio.resources import Resources

# -- Constant for the dictionary PROG, which contains
# -- the programming configuration
SERIAL_PORT = "serial_port"
FTDI_ID = "ftdi_id"
SRAM = "sram"
FLASH = "flash"


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

        # -- Split the arguments
        __, __, arch = process_arguments(args, self.resources)

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
    def graph(self, args):
        """Executes scons for visual graph generation"""

        # -- Split the arguments
        var, _, arch = process_arguments(args, self.resources)

        # -- Execute scons!!!
        # -- The packages to check are passed
        return self.run(
            "graph",
            variables=var,
            arch=arch,
            packages=["oss-cad-suite"],
        )

    @util.command
    def lint(self, args):
        """DOC: TODO"""

        config = {}
        __, __, arch = process_arguments(config, self.resources)
        var = serialize_scons_flags(
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
    def sim(self, args):
        """Simulates a testbench and shows the result in a gtkwave window."""

        # -- Split the arguments
        var, _, arch = process_arguments(args, self.resources)

        return self.run(
            "sim",
            variables=var,
            arch=arch,
            packages=["oss-cad-suite", "gtkwave"],
        )

    @util.command
    def test(self, args):
        """Tests all or a single testbench by simulating."""

        # -- Split the arguments
        var, _, arch = process_arguments(args, self.resources)

        return self.run(
            "test",
            variables=var,
            arch=arch,
            packages=["oss-cad-suite"],
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

    @util.command
    def upload(self, config: dict, prog: dict):
        """Upload the circuit to the board
        INPUTS:
          * config: Dictionary with the initial configuration
            * board
            * verbose
            * top-module
          * prog: Programming configuration parameters
            * serial_port: Serial port name
            * ftdi_id: ftdi identificator
            * sram: Perform SRAM programming
            * flash: Perform Flash programming
        OUTPUT: Exit code after executing scons
        """

        # -- Get important information from the configuration
        # -- It will raise an exception if it cannot be solved
        flags, board, arch = process_arguments(config, self.resources)

        # -- Information about the FPGA is ok!

        # -- Get the command line to execute for programming
        # -- the FPGA (programmer executable + arguments)
        # -- Ex: 'tinyprog --pyserial -c /dev/ttyACM0 --program'
        # -- Ex: 'iceprog -d i:0x0403:0x6010:0'
        programmer = self.get_programmer(board, prog)

        # -- Add as a flag to pass it to scons
        flags += [f"prog={programmer}"]

        # -- Execute Scons for uploading!
        return self.run(
            "upload",
            variables=flags,
            packages=["oss-cad-suite"],
            board=board,
            arch=arch,
        )

    def get_programmer(self, board: str, prog: dict) -> str:
        """Get the command line (string) to execute for programming
        the FPGA (programmer executable + arguments)

        * INPUT
          * board: (string): Board name
          * prog: Programming configuration params
            * serial_port: Serial port name
            * ftdi_id: ftdi identificator
            * sram: Perform SRAM programming
            * flash: Perform Flash programming

        * OUTPUT: A string with the command+args to execute
        """

        # -- Return string to create
        programmer = ""

        # -- Mandatory: There should be a board defined
        # -- If not: return!
        # -- It should not be the case bacause it has been
        # -- checked previously... but just in case....
        if not board:
            return programmer

        # -- Get the board information
        # -- Board name
        # -- FPGA
        # -- Programmer type
        # -- Programmer name
        # -- USB id  (vid, pid)
        board_data = self.resources.boards[board]

        # -- Check platform. If the platform is not compatible
        # -- with the board an exception is raised
        self.check_platform(board_data)

        # -- Check pip packages. If the corresponding pip_packages
        # -- is not installed, an exception is raised
        self.check_pip_packages(board_data)

        # -- Special case for the TinyFPGA on MACOS platforms
        # -- TinyFPGA BX board is not detected in MacOS HighSierra
        if "tinyprog" in board_data:

            # -- Get the platform
            platform = util.get_systype()

            # -- darwin / darwin_arm64 platforms
            if "darwin" in platform or "darwin_arm64" in platform:

                # In this case the serial check is ignored
                # This is the command line to execute for uploading the
                # circuit
                return "tinyprog --libusb --program"

        # -- Serialize programmer command
        # -- Get a string with the command line to execute
        # -- BUT! it is a TEMPLATE string, with some parameters
        # -- that needs to be set!
        # --   * "${VID}" (optional): USB vendor id
        # --   * "${PID}" (optional): USB Product id
        # --   * "${FTDI_ID}" (optional): FTDI id
        # --   * "${SERIAL_PORT}" (optional): Serial port name
        programmer = self.serialize_programmer(
            board_data, prog[SRAM], prog[FLASH]
        )

        # -- Assign the parameters in the Template string

        # -- Replace USB vendor id
        # -- Ex. "${VID}" --> "0403"
        if "${VID}" in programmer:

            # -- Get the vendor id
            vid = board_data["usb"]["vid"]
            # -- Place the value in the command string
            programmer = programmer.replace("${VID}", vid)

        # -- Replace USB product id
        # -- Ex. "${PID}" --> "6010"
        if "${PID}" in programmer:

            # -- Get the product id
            pid = board_data["usb"]["pid"]
            # -- Place the value in the command string
            programmer = programmer.replace("${PID}", pid)

        # -- Replace FTDI index
        # -- Ex. "${FTDI_ID}" --> "0"
        if "${FTDI_ID}" in programmer:

            # -- Check that the board is connected
            # -- If not, an exception is raised
            self.check_usb(board, board_data)

            # -- Get the FTDI index of the connected board
            ftdi_id = self.get_ftdi_id(board, board_data, prog[FTDI_ID])

            # -- Place the value in the command string
            programmer = programmer.replace("${FTDI_ID}", ftdi_id)

        # Replace Serial port
        # -- The board uses a Serial port for uploading the circuit
        if "${SERIAL_PORT}" in programmer:

            # -- Check that the board is connected
            self.check_usb(board, board_data)

            # -- Get the serial port
            device = self.get_serial_port(board, board_data, prog[SERIAL_PORT])

            # -- Place the value in the command string
            programmer = programmer.replace("${SERIAL_PORT}", device)

        # -- Return the Command to execute for uploading the circuit
        # -- to the given board
        return programmer

    @staticmethod
    def check_platform(board_data: dict) -> None:
        """Check if the current board is compatible with the
        current platform. There are some boards, like icoboard,
        that only runs in the platform linux/arm7
        * INPUT:
          * board_data: Dictionary with board information
            * Board name
            * FPGA
            * Programmer type
            * Programmer name
            * USB id  (vid, pid)

        Only in case the platform is not compatible with the board,
        and exception is raised
        """

        # -- Normal case: the board does not have a special platform
        # -- (it can be used in many platforms)
        if "platform" not in board_data:
            return

        # -- Get the platform were the board should be used
        platform = board_data["platform"]

        # -- Get the current platform
        current_platform = util.get_systype()

        # -- Check if they are not compatible!
        if platform != current_platform:

            # Incorrect platform
            if platform == "linux_armv7l":
                raise ValueError("incorrect platform: RPI2 or RPI3 required")

            raise ValueError(f"incorrect platform {platform}")

    def check_pip_packages(self, board_data):
        """Check if the corresponding pip package with the programmer
        has already been installed. In the case of an apio package
        it is just ignored

        * INPUT:
          * board_data: Dictionary with board information
            * Board name
            * FPGA
            * Programmer type
            * Programmer name
            * USB id  (vid, pid)
        """

        # -- Get the programmer object for the given board
        prog_info = board_data["programmer"]

        # -- Get the programmer type
        prog_type = prog_info["type"]

        # -- Get the programmer information
        # -- Command, arguments, pip package, etc...
        prog_data = self.resources.programmers[prog_type]

        # -- Get all the pip packages from the distribution
        all_pip_packages = self.resources.distribution["pip_packages"]

        # -- Get the name of the pip package of the current programmer,
        # -- if any (The programmer maybe in a pip package or an apio package)
        pip_packages = prog_data.get("pip_packages") or []

        # -- Check if pip package was installed
        # -- In case of an apio package it is just ignored
        for pip_pkg in pip_packages:

            # -- Get legacy string (Ex. ">=1.0.21,<1.1.0")
            legacy_str = all_pip_packages[pip_pkg]

            # -- Convert it into a legacy object
            spec = semantic_version.Spec(legacy_str)

            # -- Get package version
            try:
                pkg_version = importlib.metadata.version(pip_pkg)

            except importlib.metadata.PackageNotFoundError as exc:
                click.secho(f"Error: '{pip_pkg}' is not installed", fg="red")
                click.secho(
                    "Please run:\n" f"   pip install -U apio[{pip_pkg}]",
                    fg="yellow",
                )
                raise ValueError("Package not installed") from exc

            # -- Check pip_package version
            version = semantic_version.Version(pkg_version)

            # -- Version does not match!
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

            # -- Check pip_package itself
            try:
                __import__(pip_pkg)

            # -- Exit if a package is not working
            except ModuleNotFoundError as exc:

                # -- Get a string with the python version
                python_version = util.get_python_version()

                # -- Construct the error message
                message = f"'{pip_pkg}' not compatible with "
                message += f"Python {python_version}"
                message += f"\n       {exc}"

                # -- Raise an exception
                raise ValueError(message) from exc

    def serialize_programmer(
        self, board_data: dict, sram: bool, flash: bool
    ) -> str:
        """
        * INPUT:
          * board_data: Dictionary with board information
            * Board name
            * FPGA
            * Programmer type
            * Programmer name
            * USB id  (vid, pid)
          * sram: Perform sram programming
          * flash: Perform flash programming
        * OUTPUT: It returns a template string with the command line
           to execute for uploading the circuit. It has the following
           parameters (in the string):
           * "${VID}" (optional): USB vendor id
           * "${PID}" (optional): USB Product id
           * "${FTDI_ID}" (optional): FTDI id
           * "${SERIAL_PORT}" (optional): Serial port name

          Example of output strings:
          "'tinyprog --pyserial -c ${SERIAL_PORT} --program'"
          "'iceprog -d i:0x${VID}:0x${PID}:${FTDI_ID}'"
        """

        # -- Get the programmer type
        # -- Ex. type: "tinyprog"
        # -- Ex. type: "iceprog"
        prog_info = board_data["programmer"]
        prog_type = prog_info["type"]

        # -- Get all the information for that type of programmer
        # -- * command
        # -- * arguments
        # -- * pip package
        content = self.resources.programmers[prog_type]

        # -- Get the command (without arguments) to execute
        # -- for programming the current board
        # -- Ex. "tinyprog"
        # -- Ex. "iceprog"
        programmer = content["command"]

        # -- Let's add the arguments for executing the programmer
        if content.get("args"):
            programmer += f" {content['args']}"

        # -- Some tools need extra arguments
        # -- (like dfu-util for example)
        if prog_info.get("extra_args"):
            programmer += f" {prog_info['extra_args']}"

        # -- Special cases for different programmers

        # -- Enable SRAM programming
        if sram:

            # Only for iceprog programmer
            if programmer.startswith("iceprog"):
                programmer += " -S"

        # -- Enable FLASH programming
        if flash:

            # Only for ujprog programmer
            if programmer.startswith("ujprog"):
                programmer = programmer.replace("SRAM", "FLASH")

        return programmer

    @staticmethod
    def check_usb(board: str, board_data: dict) -> None:
        """Check if the given board is connected or not to the computer
           If it is not connected, an exception is raised

        * INPUT:
          * board: Board name (string)
          * board_data: Dictionary with board information
            * Board name
            * FPGA
            * Programmer type
            * Programmer name
            * USB id  (vid, pid)
        """

        # -- The board is connected by USB
        # -- If it does not have the "usb" property, it means
        # -- the board configuration is wrong...Raise an exception
        if "usb" not in board_data:
            raise AttributeError("Missing board configuration: usb")

        # -- Get the vid and pid from the configuration
        # -- Ex. {'vid': '0403', 'pid':'6010'}
        usb_data = board_data["usb"]

        # -- Create a string with vid, pid in the format "vid:pid"
        hwid = f"{usb_data['vid']}:{usb_data['pid']}"

        # -- Get the list of the connected USB devices
        # -- (execute the command "lsusb" from the apio System module)
        system = System()
        connected_devices = system.get_usb_devices()

        # -- Check if the given device (vid:pid) is connected!
        # -- Not connected by default
        found = False

        for usb_device in connected_devices:

            # -- Device found! Board connected!
            if usb_device["hwid"] == hwid:
                found = True
                break

        # -- The board is NOT connected
        if not found:

            # -- Special case! TinyFPGA board
            # -- Maybe the board is NOT detected because
            # -- the user has not press the reset button and the bootloader
            # -- is not active
            if "tinyprog" in board_data:
                click.secho(
                    "Activate bootloader by pressing the reset button",
                    fg="yellow",
                )

            # -- Raise an exception
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

    def get_ftdi_id(self, board, board_data, ext_ftdi_id) -> str:
        """Get the FTDI index of the detected board

        * INPUT:
          * board: Board name (string)
          * board_data: Dictionary with board information
            * Board name
            * FPGA
            * Programmer type
            * Programmer name
            * USB id  (vid, pid)
          * ext_ftdi_id: FTDI index given by the user (optional)

        * OUTPUT: It return the FTDI index (as a string)
                  Ex: '0'

          It raises an exception if no FTDI device is connected
        """

        # -- Search device by FTDI id
        ftdi_id = self._check_ftdi(board, board_data, ext_ftdi_id)

        # -- No FTDI board connected
        if ftdi_id is None:
            raise AttributeError("board " + board + " not connected")

        # -- Return the FTDI index
        # -- Ex: '0'
        return ftdi_id

    @staticmethod
    def _check_ftdi(board, board_data, ext_ftdi_id) -> str:
        """Check if the given ftdi board is connected or not to the computer
           and return its FTDI index

        * INPUT:
          * board: Board name (string)
          * board_data: Dictionary with board information
            * Board name
            * FPGA
            * Programmer type
            * Programmer name
            * USB id  (vid, pid)
          * ext_ftdi_id: FTDI index given by the user (optional)

        * OUTPUT: It return the FTDI index (as a string)
                  Ex: '0'
              * Or None if no board is found
        """

        # -- Check that the given board has the property "ftdi"
        # -- If not, it is an error. Raise an exception
        if "ftdi" not in board_data:
            raise AttributeError("Missing board configuration: ftdi")

        # -- Get the board description from the the apio database
        board_desc = board_data["ftdi"]["desc"]

        # -- Build a regular expresion for finding this board
        # -- description in the connected board
        # -- Ex: '^Alhambra II.*$'
        # -- Notes on regular expresions:
        # --   ^  --> Means the begining of the string
        # --   .  --> Any character
        # --   .* --> zero or many characters
        # --   $  --> End of string
        desc_pattern = f"^{board_desc}.*$"

        # -- Get the list of the connected FTDI devices
        # -- (execute the command "lsftdi" from the apio System module)
        system = System()
        connected_devices = system.get_ftdi_devices()

        # -- No FTDI devices detected --> Error!
        if not connected_devices:

            # -- Board not available
            raise AttributeError("board " + board + " not available")

        # -- Check if the given board is connected
        # -- and if so, return its FTDI index
        for ftdi_device in connected_devices:

            # -- Get the FTDI index
            # -- Ex: '0'
            index = ftdi_device["index"]

            # If the --device options is set but it doesn't match
            # with the detected index, skip the port.
            if ext_ftdi_id is not None and ext_ftdi_id != index:
                continue

            # If matches the description pattern
            # return the index for the FTDI device.
            if re.match(desc_pattern, ftdi_device["description"]):
                return index

        # -- No FTDI board found
        return None

    # R0913: Too many arguments (6/5)
    # pylint: disable=R0913
    def run(self, command, variables, packages, board=None, arch=None):
        """Executes scons"""

        # -- Check if in the current project a custom SConstruct file
        # is being used. We fist build the full name (with the full path)
        scon_file = Path.cwd() / "SConstruct"

        # -- If the SConstruct file does NOT exist, we use the one provided by
        # -- apio, which is located in the resources/arch/ folder
        if not scon_file.exists():
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
    def _execute_scons(self, command: str, variables, board):
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
