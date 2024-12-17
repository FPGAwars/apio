"""DOC: TODO"""

# C0302: Too many lines in module (1032/1000) (too-many-lines)
# pylint: disable=C0302

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import os
import re
import time
import datetime
import shutil
from functools import wraps

import importlib.metadata
import click
import semantic_version

from apio import util
from apio import pkg_util
from apio.managers.scons_args import process_arguments
from apio.managers.system import System
from apio.apio_context import ApioContext
from apio.managers.scons_filter import SconsFilter

# -- Constant for the dictionary PROG, which contains
# -- the programming configuration
SERIAL_PORT = "serial_port"
FTDI_ID = "ftdi_id"
SRAM = "sram"
FLASH = "flash"

# -- ANSI Constants
CURSOR_UP = "\033[F"
ERASE_LINE = "\033[K"


# W0703: Catching too general exception Exception (broad-except)
# pylint: disable=W0703
# pylint: disable=W0150
#
# -- Based on
# -- https://stackoverflow.com/questions/5929107/decorators-with-parameters
def on_exception(*, exit_code: int):
    """Decoractor for functions that return int exit code. If the function
    throws an exception, the error message is printed, and the caller see the
    returned value exit_code instead of the exception.
    """

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as exc:
                # For debugging. Uncomment to print the exception's stack.
                # import traceback
                # traceback.print_tb(exc.__traceback__)

                if str(exc):
                    click.secho("Error: " + str(exc), fg="red")
                return exit_code

        return wrapper

    return decorator


class SCons:
    """Class for managing the scons tools"""

    def __init__(self, apio_ctx: ApioContext):
        """Initialization."""
        # -- Cache the apio context.
        self.apio_ctx = apio_ctx

        # -- Change to the project's folder.
        os.chdir(apio_ctx.project_dir)

    @on_exception(exit_code=1)
    def clean(self, args) -> int:
        """Runs a scons subprocess with the 'clean' target. Returns process
        exit code, 0 if ok."""

        # -- Split the arguments
        variables, __, arch = process_arguments(self.apio_ctx, args)

        # --Clean the project: run scons -c (with aditional arguments)
        return self._run(
            "-c", arch=arch, variables=variables, required_packages_names=[]
        )

    @on_exception(exit_code=1)
    def verify(self, args) -> int:
        """Runs a scons subprocess with the 'verify' target. Returns process
        exit code, 0 if ok."""

        # -- Split the arguments
        variables, __, arch = process_arguments(self.apio_ctx, args)

        # -- Execute scons!!!
        # -- The packages to check are passed
        return self._run(
            "verify",
            variables=variables,
            arch=arch,
            required_packages_names=["oss-cad-suite"],
        )

    @on_exception(exit_code=1)
    def graph(self, args) -> int:
        """Runs a scons subprocess with the 'graph' target. Returns process
        exit code, 0 if ok."""

        # -- Split the arguments
        variables, _, arch = process_arguments(self.apio_ctx, args)

        # -- Execute scons!!!
        # -- The packages to check are passed
        return self._run(
            "graph",
            variables=variables,
            arch=arch,
            required_packages_names=["oss-cad-suite", "graphviz"],
        )

    @on_exception(exit_code=1)
    def lint(self, args) -> int:
        """Runs a scons subprocess with the 'lint' target. Returns process
        exit code, 0 if ok."""

        variables, __, arch = process_arguments(self.apio_ctx, args)
        return self._run(
            "lint",
            variables=variables,
            arch=arch,
            required_packages_names=["oss-cad-suite"],
        )

    @on_exception(exit_code=1)
    def sim(self, args) -> int:
        """Runs a scons subprocess with the 'sim' target. Returns process
        exit code, 0 if ok."""

        # -- Split the arguments
        variables, _, arch = process_arguments(self.apio_ctx, args)

        return self._run(
            "sim",
            variables=variables,
            arch=arch,
            required_packages_names=["oss-cad-suite"],
        )

    @on_exception(exit_code=1)
    def test(self, args) -> int:
        """Runs a scons subprocess with the 'test' target. Returns process
        exit code, 0 if ok."""

        # -- Split the arguments
        variables, _, arch = process_arguments(self.apio_ctx, args)

        return self._run(
            "test",
            variables=variables,
            arch=arch,
            required_packages_names=["oss-cad-suite"],
        )

    @on_exception(exit_code=1)
    def build(self, args) -> int:
        """Runs a scons subprocess with the 'build' target. Returns process
        exit code, 0 if ok."""

        # -- Split the arguments
        variables, board, arch = process_arguments(self.apio_ctx, args)

        # -- Execute scons!!!
        # -- The packages to check are passed
        return self._run(
            "build",
            variables=variables,
            board=board,
            arch=arch,
            required_packages_names=["oss-cad-suite"],
        )

    @on_exception(exit_code=1)
    def time(self, args) -> int:
        """Runs a scons subprocess with the 'time' target. Returns process
        exit code, 0 if ok."""

        variables, board, arch = process_arguments(self.apio_ctx, args)

        if arch not in ["ice40"]:
            click.secho(
                "Error: Time analysis for "
                f"{arch.upper()} is not supported yet.",
                fg="red",
            )
            return 99

        return self._run(
            "time",
            variables=variables,
            board=board,
            arch=arch,
            required_packages_names=["oss-cad-suite"],
        )

    @on_exception(exit_code=1)
    def report(self, args) -> int:
        """Runs a scons subprocess with the 'report' target. Returns process
        exit code, 0 if ok."""

        variables, board, arch = process_arguments(self.apio_ctx, args)

        return self._run(
            "report",
            variables=variables,
            board=board,
            arch=arch,
            required_packages_names=["oss-cad-suite"],
        )

    @on_exception(exit_code=1)
    def upload(self, config: dict, prog: dict) -> int:
        """Runs a scons subprocess with the 'time' target. Returns process
        exit code, 0 if ok.

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
        """

        # -- Get important information from the configuration
        # -- It will raise an exception if it cannot be solved
        flags, board, arch = process_arguments(self.apio_ctx, config)

        # -- Information about the FPGA is ok!

        # -- Get the command line to execute for programming
        # -- the FPGA (programmer executable + arguments)
        # -- Ex: 'tinyprog --pyserial -c /dev/ttyACM0 --program'
        # -- Ex: 'iceprog -d i:0x0403:0x6010:0'
        programmer = self._get_programmer(board, prog)

        # -- Add as a flag to pass it to scons
        flags += [f"prog={programmer}"]

        # -- Execute Scons for uploading!
        exit_code = self._run(
            "upload",
            variables=flags,
            required_packages_names=["oss-cad-suite"],
            board=board,
            arch=arch,
        )

        return exit_code

    def _get_programmer(self, board: str, prog: dict) -> str:
        """Get the command line (string) to execute for programming
        the FPGA (programmer executable + arguments)

        * INPUT
          * board: (string): Board name
          * prog: Programming configuration params
            * serial_port: Serial port name
            * ftdi_id: ftdi identificator
            * sram: Perform SRAM programming
            * flash: Perform Flash programming

        * OUTPUT: A string with the command+args to execute and a $SOURCE
          placeholder for the bitstream file name.
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
        board_info = self.apio_ctx.boards[board]

        # -- Check platform. If the platform is not compatible
        # -- with the board an exception is raised
        self._check_platform(board_info, self.apio_ctx.platform_id)

        # -- Check pip packages. If the corresponding pip_packages
        # -- is not installed, an exception is raised
        self._check_pip_packages(board_info)

        # -- pylint: disable=fixme
        # -- TODO: abstract this better in boards.json. For example, add a
        # -- property "darwin-no-detection".
        # --
        # -- Special case for the TinyFPGA on MACOS platforms
        # -- TinyFPGA BX board is not detected in MacOS HighSierra
        if "tinyprog" in board_info and self.apio_ctx.is_darwin():
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
        programmer = self._serialize_programmer(
            board_info, prog[SRAM], prog[FLASH]
        )
        # -- The placeholder for the bitstream file name should always exist.
        assert "$SOURCE" in programmer, programmer

        # -- Assign the parameters in the Template string

        # -- Replace USB vendor id
        # -- Ex. "${VID}" --> "0403"
        if "${VID}" in programmer:

            # -- Get the vendor id
            vid = board_info["usb"]["vid"]
            # -- Place the value in the command string
            programmer = programmer.replace("${VID}", vid)

        # -- Replace USB product id
        # -- Ex. "${PID}" --> "6010"
        if "${PID}" in programmer:

            # -- Get the product id
            pid = board_info["usb"]["pid"]
            # -- Place the value in the command string
            programmer = programmer.replace("${PID}", pid)

        # -- Replace FTDI index
        # -- Ex. "${FTDI_ID}" --> "0"
        if "${FTDI_ID}" in programmer:
            # -- Inform the user we are accessing the programmer
            # -- to give context for ftdi failures.
            # -- We force an early env setting message to have
            # -- the programmer message closer to the error message.
            pkg_util.set_env_for_packages(
                self.apio_ctx,
            )
            click.secho("Querying programmer parameters.")

            # -- Check that the board is connected
            # -- If not, an exception is raised
            self._check_usb(board, board_info)

            # -- Get the FTDI index of the connected board
            ftdi_id = self._get_ftdi_id(board, board_info, prog[FTDI_ID])

            # -- Place the value in the command string
            programmer = programmer.replace("${FTDI_ID}", ftdi_id)

        # Replace Serial port
        # -- The board uses a Serial port for uploading the circuit
        if "${SERIAL_PORT}" in programmer:
            # -- Inform the user we are accessing the programmer
            # -- to give context for ftdi failures.
            # -- We force an early env setting message to have
            # -- the programmer message closer to the error message.
            pkg_util.set_env_for_packages(self.apio_ctx)
            click.secho("Querying serial port parameters.")

            # -- Check that the board is connected
            self._check_usb(board, board_info)

            # -- Get the serial port
            device = self._get_serial_port(
                board, board_info, prog[SERIAL_PORT]
            )

            # -- Place the value in the command string
            programmer = programmer.replace("${SERIAL_PORT}", device)

        # -- Return the Command to execute for uploading the circuit
        # -- to the given board. Scons will replace $SOURCE with the
        # -- bitstream file name before executing the command.
        assert "$SOURCE" in programmer, programmer
        return programmer

    @staticmethod
    def _check_platform(board_info: dict, actual_platform_id: str) -> None:
        """Check if the current board is compatible with the
        current platform. There are some boards, like icoboard,
        that only runs in the platform linux/arm7
        * INPUT:
          * board_info: Dictionary with board info from boards.json.

        Only in case the platform is not compatible with the board,
        and exception is raised
        """

        # -- Normal case: the board does not have a special platform
        # -- (it can be used in many platforms)
        if "platform" not in board_info:
            return

        # -- Get the platform were the board should be used
        required_platform_id = board_info["platform"]

        # -- Check if they are not compatible!
        if actual_platform_id != required_platform_id:

            # Incorrect platform
            if actual_platform_id == "linux_armv7l":
                raise ValueError("incorrect platform: RPI2 or RPI3 required")

            raise ValueError(
                "Board is restricted to platform "
                f"'{required_platform_id}' but '{actual_platform_id}' found."
            )

    def _check_pip_packages(self, board_info):
        """Check if the corresponding pip package with the programmer
        has already been installed. In the case of an apio package
        it is just ignored

        * INPUT:
          * board_info: Dictionary with board info from boards.json.
        """

        # -- Get the programmer object for the given board
        prog_info = board_info["programmer"]

        # -- Get the programmer type
        prog_type = prog_info["type"]

        # -- Get the programmer information
        # -- Command, arguments, pip package, etc...
        prog_data = self.apio_ctx.programmers[prog_type]

        # -- Get all the pip packages from the distribution
        all_pip_packages = self.apio_ctx.distribution["pip_packages"]

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

    def _serialize_programmer(
        self, board_info: dict, sram: bool, flash: bool
    ) -> str:
        """
        * INPUT:
          * board_info: Dictionary with board info from boards.json.
        * OUTPUT: It returns a template string with the command line
           to execute for uploading the circuit. It has the following
           parameters (in the string):
           * "${VID}" (optional): USB vendor id
           * "${PID}" (optional): USB Product id
           * "${FTDI_ID}" (optional): FTDI id
           * "${SERIAL_PORT}" (optional): Serial port name

          Example of output strings:
          "'tinyprog --pyserial -c ${SERIAL_PORT} --program $SOURCE'"
          "'iceprog -d i:0x${VID}:0x${PID}:${FTDI_ID} $SOURCE'"
        """

        # -- Get the programmer type
        # -- Ex. type: "tinyprog"
        # -- Ex. type: "iceprog"
        prog_info = board_info["programmer"]
        prog_type = prog_info["type"]

        # -- Get all the information for that type of programmer
        # -- * command
        # -- * arguments
        # -- * pip package
        content = self.apio_ctx.programmers[prog_type]

        # -- Get the command (without arguments) to execute
        # -- for programming the current board
        # -- Ex. "tinyprog"
        # -- Ex. "iceprog"
        programmer = content["command"]

        # -- Let's add the arguments for executing the programmer
        if content.get("args"):
            programmer += f" {content['args']}"

        # -- Mark the expected location of the bitstream file name, before
        # -- we appened any arg to the command. Some programmers such as
        # -- dfu-util require it immediatly after the "args" string.
        programmer += " $SOURCE"

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

    def _check_usb(self, board: str, board_info: dict) -> None:
        """Check if the given board is connected or not to the computer
           If it is not connected, an exception is raised

        * INPUT:
          * board: Board name (string)
          * board_info: Dictionary with board info from boards.json.
        """

        # -- The board is connected by USB
        # -- If it does not have the "usb" property, it means
        # -- the board configuration is wrong...Raise an exception
        if "usb" not in board_info:
            raise AttributeError("Missing board configuration: usb")

        # -- Get the vid and pid from the configuration
        # -- Ex. {'vid': '0403', 'pid':'6010'}
        usb_data = board_info["usb"]

        # -- Create a string with vid, pid in the format "vid:pid"
        hwid = f"{usb_data['vid']}:{usb_data['pid']}"

        # -- Get the list of the connected USB devices
        # -- (execute the command "lsusb" from the apio System module)
        system = System(self.apio_ctx)
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
            if "tinyprog" in board_info:
                click.secho(
                    "Activate bootloader by pressing the reset button",
                    fg="yellow",
                )

            # -- Raise an exception
            raise ConnectionError("board " + board + " not connected")

    def _get_serial_port(
        self, board: str, borad_info: dict, ext_serial_port: str
    ) -> str:
        """Get the serial port of the connected board
        * INPUT:
          * board: Board name (string)
          * board_info: Dictionary with board info from boards.json.
          * ext_serial_port: serial port name given by the user (optional)

        * OUTPUT: (string) The serial port name

        It raises an exception if the board is not connected
        """

        # -- Search Serial port by USB id
        device = self._check_serial(board, borad_info, ext_serial_port)

        # -- Board not connected
        if not device:
            raise ConnectionError("board " + board + " not connected")

        # -- Board connected. Return the serial port detected
        return device

    def _check_serial(
        self, board: str, board_info: dict, ext_serial_port: str
    ) -> str:
        """Check the that the serial port for the given board exists
         (board connedted)

        * INPUT:
          * board: Board name (string)
          * board_info: Dictionary with board info from boards.json.
          * ext_serial_port: serial port name given by the user (optional)

        * OUTPUT: (string) The serial port name
        """

        # -- The board is connected by USB
        # -- If it does not have the "usb" property, it means
        # -- the board configuration is wrong...Raise an exception
        if "usb" not in board_info:
            raise AttributeError("Missing board configuration: usb")

        # -- Get the vid and pid from the configuration
        # -- Ex. {'vid': '0403', 'pid':'6010'}
        usb_data = board_info["usb"]

        # -- Create a string with vid, pid in the format "vid:pid"
        hwid = f"{usb_data['vid']}:{usb_data['pid']}"

        # -- Get the list of the connected serial ports
        # -- Ex: [{'port': '/dev/ttyACM0',
        #          'description': 'ttyACM0',
        #          'hwid': 'USB VID:PID=1D50:6130 LOCATION=1-5:1.0'}]
        serial_ports = util.get_serial_ports()

        # -- If no serial ports detected: raise an Error!
        if not serial_ports:

            # Board not available
            raise AttributeError("board " + board + " not available")

        # -- Match the discovered serial ports
        for serial_port_data in serial_ports:

            # -- Get the port name of the detected board
            port = serial_port_data["port"]

            # If the --device options is set but it doesn't match
            # the detected port, skip the port.
            if ext_serial_port and ext_serial_port != port:
                continue

            # -- Check if the TinyFPGA board is connected
            connected = self._check_tinyprog(board_info, port)

            # -- If the usb id matches...
            if hwid.lower() in serial_port_data["hwid"].lower():

                # -- Special case: TinyFPGA. Ignore usb id if
                # -- board not detected
                if "tinyprog" in board_info and not connected:
                    continue

                # -- Return the serial port
                return port

        # -- No serial port found...
        return None

    @staticmethod
    def _check_tinyprog(board_info: dict, port: str) -> bool:
        """Check if the correct TinyFPGA board is connected
        * INPUT:
          * board_info: Dictionary with board info from boards.json.
          * port: Serial port name

        * OUTPUT:
          * True: TinyFPGA detected
          * False: TinyFPGA not detected
        """

        # -- Check that the given board has the property "tinyprog"
        # -- If not, return False
        if "tinyprog" not in board_info:
            return False

        # -- Get the board description from the the apio database
        board_desc = board_info["tinyprog"]["desc"]

        # -- Build a regular expresion for finding this board
        # -- description in the connected board
        # -- Ex: '^TinyFPGA BX$'
        # -- Notes on regular expresions:
        # --   ^  --> Means the begining of the string
        # --   $  --> End of string
        desc_pattern = f"^{board_desc}$"

        # -- Get a list with the meta data of all the TinyFPGA boards
        # -- connected
        list_meta = util.get_tinyprog_meta()

        # -- Check if there is a match: target TinyFPGA is ok
        for tinyprog_meta in list_meta:

            # -- Get the serial port name
            tinyprog_port = tinyprog_meta["port"]

            # -- Get the name of the connected board
            tinyprog_name = tinyprog_meta["boardmeta"]["name"]

            # -- # If the port is detected and it matches the pattern
            if port == tinyprog_port and re.match(desc_pattern, tinyprog_name):

                # -- TinyFPGA board detected!
                return True

        # -- TinyFPGA board not detected!
        return False

    def _get_ftdi_id(self, board, board_info, ext_ftdi_id) -> str:
        """Get the FTDI index of the detected board

        * INPUT:
          * board: Board name (string)
          * board_info: Dictionary with board info from boards.json.
          * ext_ftdi_id: FTDI index given by the user (optional)

        * OUTPUT: It return the FTDI index (as a string)
                  Ex: '0'

          It raises an exception if no FTDI device is connected
        """

        # -- Search device by FTDI id
        ftdi_id = self._check_ftdi(board, board_info, ext_ftdi_id)

        # -- No FTDI board connected
        if ftdi_id is None:
            raise AttributeError("board " + board + " not connected")

        # -- Return the FTDI index
        # -- Ex: '0'
        return ftdi_id

    def _check_ftdi(
        self, board: str, board_info: dict, ext_ftdi_id: str
    ) -> str:
        """Check if the given ftdi board is connected or not to the computer
           and return its FTDI index

        * INPUT:
          * board: Board name (string)
          * board_info: Dictionary with board info from boards.json.
          * ext_ftdi_id: FTDI index given by the user (optional)

        * OUTPUT: It return the FTDI index (as a string)
                  Ex: '0'
              * Or None if no board is found
        """

        # -- Check that the given board has the property "ftdi"
        # -- If not, it is an error. Raise an exception
        if "ftdi" not in board_info:
            raise AttributeError("Missing board configuration: ftdi")

        # -- Get the board description from the the apio database
        board_desc = board_info["ftdi"]["desc"]

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
        system = System(self.apio_ctx)
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

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def _run(
        self,
        command,
        variables,
        required_packages_names,
        board=None,
        arch=None,
    ):
        """Executes scons"""

        # -- Construct the path to the SConstruct file.
        scons_dir = util.get_path_in_apio_package("scons")
        scons_file_path = scons_dir / arch / "SConstruct"

        # -- It is passed to scons using the flag -f default_scons_file
        variables += ["-f", f"{scons_file_path}"]

        # -- Check that the required packages are installed
        pkg_util.check_required_packages(
            self.apio_ctx, required_packages_names
        )

        # -- Set env path and vars to use the packages.
        pkg_util.set_env_for_packages(self.apio_ctx)

        # -- Execute scons
        return self._execute_scons(command, variables, board)

    # R0914: Too many local variables (19/15)
    # pylint: disable=R0914
    def _execute_scons(self, command: str, variables: list, board: str) -> int:
        """Execute the scons builder
        * INPUTS:
          * command: (string): Apio command. Ex. 'upload', 'build'...
          * variables: Parameters passed to scons
            Ex. ['fpga_arch=ice40', 'fpga_size=8k', 'fpga_type=lp',
                 'fpga_pack=cm81', 'top_module=main',
                 'prog=tinyprog --pyserial -c /dev/ttyACM0 --program',
                 '-f', '/home/obijuan/Develop/FPGAwars/apio/apio/
                        scons/ice40/SConstruct']
          * board: (string) Board name

        * OUTPUT: Exit code
           * 0: SUCESS!!
           * x: Error
        """

        # -- Get the terminal width (typically 80)
        terminal_width, _ = shutil.get_terminal_size()

        # -- Read the time (for measuring how long does it take
        # -- to execute the apio command)
        start_time = time.time()

        # -- Only for these three commands
        if command in ("build", "upload", "time"):

            # -- Get the type of board
            if board:
                processing_board = board
            else:
                processing_board = "custom board"

            # -- Get the date as a string
            date_time_str = datetime.datetime.now().strftime("%c")

            # -- Board name string in color
            board_color = click.style(processing_board, fg="cyan", bold=True)

            # -- Print information on the console
            click.secho(f"[{date_time_str}] Processing {board_color}")

            # -- Print a horizontal line
            click.secho("-" * terminal_width, bold=True)

        # -- Command to execute: scons -Q apio_cmd flags
        # -- Without force_colors=True, click.secho() colors from the scons
        # -- child process will be stripped out becaused they are piped out.
        scons_command = (
            ["scons"] + ["-Q", command] + variables + ["force_colors=True"]
        )

        # For debugging. Print the scons command line in a forumat that is
        # useful for the .vscode/launch.json scons debug target.
        # import json
        # print(json.dumps(scons_command))

        # -- An output filter that manupulates the scons stdout/err lines as
        # -- needed and write them to stdout.
        scons_filter = SconsFilter()

        # -- Execute the scons builder!
        result = util.exec_command(
            scons_command,
            stdout=util.AsyncPipe(scons_filter.on_stdout_line),
            stderr=util.AsyncPipe(scons_filter.on_stderr_line),
        )

        # -- Is there an error? True/False
        is_error = result.exit_code != 0

        # -- Calculate the time it took to execute the command
        duration = time.time() - start_time

        # -- Summary
        summary_text = f" Took {duration:.2f} seconds "

        # -- Half line
        half_line = "=" * int(((terminal_width - len(summary_text) - 10) / 2))

        # -- Status message
        status = (
            click.style(" ERROR ", fg="red", bold=True)
            if is_error
            else click.style("SUCCESS", fg="green", bold=True)
        )

        # -- Print the summary line.
        click.secho(
            f"{half_line} [{status}]{summary_text}{half_line}", err=is_error
        )

        # -- Return the exit code
        return result.exit_code
