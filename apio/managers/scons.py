"""DOC: TODO"""

# C0302: Too many lines in module (1032/1000) (too-many-lines)
# pylint: disable=C0302

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import traceback
import os
import sys
import re
import time
from pathlib import Path
import shutil
from functools import wraps
from datetime import datetime


import click
from click import secho
from google.protobuf import text_format


from apio.utils import util, pkg_util
from apio.managers.system import System
from apio.apio_context import ApioContext
from apio.managers.scons_filter import SconsFilter
from apio.managers import installer
from apio.profile import Profile
from apio.proto.apio_pb2 import (
    Verbosity,
    Envrionment,
    SconsParams,
    CommandInfo,
    FpgaInfo,
    Project,
    Ice40FpgaInfo,
    Ecp5FpgaInfo,
    GowinFpgaInfo,
    ApioArch,
    CmdGraphInfo,
)

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
                if util.is_debug():
                    traceback.print_tb(exc.__traceback__)

                if str(exc):
                    secho("Error: " + str(exc), fg="red")
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
    def clean(self) -> int:
        """Runs a scons subprocess with the 'clean' target. Returns process
        exit code, 0 if ok."""

        scons_params = self.construct_scons_params()

        # --Clean the project: run scons -c (with aditional arguments)
        return self._run("-c", scons_params=scons_params, uses_packages=False)

    @on_exception(exit_code=1)
    def graph(self, graph_cmd_info: CmdGraphInfo, verbosity: Verbosity) -> int:
        """Runs a scons subprocess with the 'graph' target. Returns process
        exit code, 0 if ok."""

        # -- Construct scons params with graph command info.
        scons_params = self.construct_scons_params(
            command_info=CommandInfo(graph=graph_cmd_info),
            verbosity=verbosity,
        )

        # -- Invoke the scons process.
        return self._run(
            "graph",
            scons_params=scons_params,
            uses_packages=True,
        )

    @on_exception(exit_code=1)
    def lint(self, args) -> int:
        """Runs a scons subprocess with the 'lint' target. Returns process
        exit code, 0 if ok."""

        # board, variables = process_arguments(self.apio_ctx, args)
        # return self._run(
        #     "lint",
        #     board=board,
        #     variables=variables,
        #     uses_packages=True,
        # )

    @on_exception(exit_code=1)
    def sim(self, args) -> int:
        """Runs a scons subprocess with the 'sim' target. Returns process
        exit code, 0 if ok."""

        # -- Split the arguments
        # board, variables = process_arguments(self.apio_ctx, args)

        # return self._run(
        #     "sim",
        #     board=board,
        #     variables=variables,
        #     uses_packages=True,
        # )

    @on_exception(exit_code=1)
    def test(self, args) -> int:
        """Runs a scons subprocess with the 'test' target. Returns process
        exit code, 0 if ok."""

        # # -- Split the arguments
        # board, variables = process_arguments(self.apio_ctx, args)

        # return self._run(
        #     "test",
        #     board=board,
        #     variables=variables,
        #     uses_packages=True,
        # )

    @on_exception(exit_code=1)
    def build(self, verbosity: Verbosity) -> int:
        """Runs a scons subprocess with the 'build' target. Returns process
        exit code, 0 if ok."""

        # -- Construct the scons params object.
        scons_params = self.construct_scons_params(verbosity=verbosity)
        return self._run(
            "build",
            scons_params=scons_params,
            uses_packages=True,
        )

    @on_exception(exit_code=1)
    def report(self, args) -> int:
        """Runs a scons subprocess with the 'report' target. Returns process
        exit code, 0 if ok."""

        # board, variables = process_arguments(self.apio_ctx, args)

        # return self._run(
        #     "report",
        #     board=board,
        #     variables=variables,
        #     uses_packages=True,
        # )

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

        # # -- Get important information from the configuration
        # # -- It will raise an exception if it cannot be solved
        # board, variables = process_arguments(self.apio_ctx, config)

        # # -- Information about the FPGA is ok!

        # # -- Get the command line to execute for programming
        # # -- the FPGA (programmer executable + arguments)
        # # -- Ex: 'tinyprog --pyserial -c /dev/ttyACM0 --program'
        # # -- Ex: 'iceprog -d i:0x0403:0x6010:0'
        # programmer = self._get_programmer(board, prog)

        # # -- Add as a flag to pass it to scons
        # variables += [f"prog={programmer}"]

        # # -- Execute Scons for uploading!
        # exit_code = self._run(
        #     "upload",
        #     board=board,
        #     variables=variables,
        #     uses_packages=True,
        # )

        # return exit_code

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

        # -- pylint: disable=fixme
        # -- TODO: abstract this better in boards.jsonc. For example, add a
        # -- property "darwin-no-detection".
        # --
        # -- Special case for the TinyFPGA on MACOS platforms
        # -- TinyFPGA BX board is not detected in MacOS HighSierra
        if "tinyprog" in board_info and self.apio_ctx.is_darwin():
            # In this case the serial check is ignored
            # This is the command line to execute for uploading the
            # circuit
            return "tinyprog --libusb --program $SOURCE"

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
            secho("Querying programmer parameters.")

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
            secho("Querying serial port parameters.")

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

    # @staticmethod
    # def _check_platform(board_info: dict, actual_platform_id: str) -> None:
    #     """Check if the current board is compatible with the
    #     current platform. There are some boards, like icoboard,
    #     that only runs in the platform linux/arm7
    #     * INPUT:
    #       * board_info: Dictionary with board info from boards.jsonc.

    #     Only in case the platform is not compatible with the board,
    #     and exception is raised
    #     """

    #     # -- Normal case: the board does not have a special platform
    #     # -- (it can be used in many platforms)
    #     if "platform" not in board_info:
    #         return

    #     # -- Get the platform were the board should be used
    #     required_platform_id = board_info["platform"]

    #     # -- Check if they are not compatible!
    #     if actual_platform_id != required_platform_id:

    #         raise ValueError(
    #             "Board is restricted to platform "
    #             f"'{required_platform_id}' but '{actual_platform_id}' found."
    #         )

    def _serialize_programmer(
        self, board_info: dict, sram: bool, flash: bool
    ) -> str:
        """
        * INPUT:
          * board_info: Dictionary with board info from boards.jsonc.
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
          * board_info: Dictionary with board info from boards.jsonc.
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
                secho(
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
          * board_info: Dictionary with board info from boards.jsonc.
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
          * board_info: Dictionary with board info from boards.jsonc.
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
          * board_info: Dictionary with board info from boards.jsonc.
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
          * board_info: Dictionary with board info from boards.jsonc.
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
          * board_info: Dictionary with board info from boards.jsonc.
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

    def construct_scons_params(
        self,
        *,
        command_info: CommandInfo = None,
        verbosity: Verbosity = None,
    ) -> SconsParams:
        """Populate and return the SconsParam proto to pass to the scons
        process."""

        # -- Create a shortcut.
        apio_ctx = self.apio_ctx

        # -- Create an empty proto object that will be populated.
        result = SconsParams()

        # -- Populate the timestamp. We use to to make sure scons reads the
        # -- correct version of the scons.params file.
        ts = datetime.now()
        result.timestamp = ts.strftime("%d%H%M%S%f")[:-3]

        # -- Get the project data. All commands that invoke scons are expected
        # -- to be in a project context.
        assert apio_ctx.has_project, "Scons encountered a missing project."
        project = apio_ctx.project

        # -- Get the project's board. It should be prevalidated when loading
        # -- the project, but we sanity check it again just in case.
        board = project["board"]
        assert board is not None, "Scons got a None board."
        assert board in apio_ctx.boards, f"Unknown board name [{board}]"

        # -- Get the project fpga id from the board info.
        fpga_id = apio_ctx.boards.get(board).get("fpga")
        assert fpga_id, "construct_scons_params(): fpga assertion failed."
        assert (
            fpga_id in apio_ctx.fpgas
        ), f"construct_scons_params(): unknown fpga {fpga_id} "
        fpga_config = apio_ctx.fpgas.get(fpga_id)
        fpga_arch = fpga_config["arch"]

        # -- Populate the common values of FpgaInfo.
        result.fpga_info.MergeFrom(
            FpgaInfo(
                fpga_id=fpga_id,
                part_num=fpga_config["part_num"],
                size=fpga_config["size"],
            )
        )

        # - Populate the architecture specific values of result.fpga_info.
        if fpga_arch == "ice40":
            result.arch = ApioArch.ICE40
            result.fpga_info.ice40.MergeFrom(
                Ice40FpgaInfo(
                    type=fpga_config["type"], pack=fpga_config["pack"]
                )
            )
        elif fpga_arch == "ecp5":
            result.arch = ApioArch.ECP5
            result.fpga_info.ecp5.MergeFrom(
                Ecp5FpgaInfo(
                    type=fpga_config["type"],
                    pack=fpga_config["pack"],
                    speed=fpga_config["speed"],
                )
            )
        elif fpga_arch == "gowin":
            result.arch = ApioArch.GOWIN
            result.fpga_info.gowin.MergeFrom(
                GowinFpgaInfo(family=fpga_config["type"])
            )
        else:
            secho(
                f"Internal error: unexpected fpga_arch value {fpga_arch}",
                fg="red",
            )
            sys.exit(1)

        # -- We are done populating The FpgaInfo params..
        assert result.fpga_info.IsInitialized()

        # -- Populate the optional Verbosity params.
        if verbosity:
            result.verbosity.MergeFrom(verbosity)
            assert result.verbosity.IsInitialized()

        # -- Populate the Environment params.
        assert apio_ctx.platform_id, "Missing platform_id in apio context"
        oss_vars = apio_ctx.all_packages["oss-cad-suite"]["env"]["vars"]

        result.envrionment.MergeFrom(
            Envrionment(
                platform_id=apio_ctx.platform_id,
                is_debug=util.is_debug(),
                yosys_path=oss_vars["YOSYS_LIB"],
                trellis_path=oss_vars["TRELLIS"],
            )
        )
        assert result.envrionment.IsInitialized()

        # -- Populate the Project params.
        result.project.MergeFrom(
            Project(
                board_id=project["board"], top_module=project["top-module"]
            )
        )
        assert result.project.IsInitialized()

        # -- Populate the optinal command specific params.
        if command_info:
            result.cmds.MergeFrom(command_info)
            assert result.cmds.IsInitialized()

        # -- All done.
        assert result.IsInitialized()
        return result

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def _run(
        self,
        scond_command: str,
        *,
        scons_params: SconsParams = None,
        uses_packages: bool,
    ):
        """Invoke an scons subprocess."""

        # -- Pass to the scons process the name of the sconstruct file it
        # -- should use.
        scons_dir = util.get_path_in_apio_package("scons")
        scons_file_path = scons_dir / "SConstruct"
        variables = ["-f", f"{scons_file_path}"]

        # -- Pass to the wscons process the timestamp of the scons params we
        # -- pass via a file. This is for verification purposes only.
        variables += [f"timestamp={scons_params.timestamp}"]

        # -- If the apio packages are required for this command, install them
        # -- if needed.
        if uses_packages:
            installer.install_missing_packages_on_the_fly(self.apio_ctx)

        # -- We set the env variables also for a command such as 'clean'
        # -- which doesn't use the packages, to satisfy the required env
        # -- variables of the scons arg parser.
        pkg_util.set_env_for_packages(self.apio_ctx)

        if util.is_debug():
            secho("\nSCONS CALL:", fg="magenta")
            secho(f"* command:       {scond_command}")
            secho(f"* variables:     {variables}")
            secho(f"* uses packages: {uses_packages}")
            secho(f"* scons params: \n{scons_params}")
            secho()

        # -- Get the terminal width (typically 80)
        terminal_width, _ = shutil.get_terminal_size()

        # -- Read the time (for measuring how long does it take
        # -- to execute the apio command)
        start_time = time.time()

        # -- Get the date as a string
        date_time_str = datetime.now().strftime("%c")

        # -- Board name string in color
        board_color = click.style(
            scons_params.project.board_id, fg="cyan", bold=True
        )

        # -- Print information on the console
        secho(f"[{date_time_str}] Processing {board_color}")

        # -- Print a horizontal line
        secho("-" * terminal_width, bold=True)

        # -- Create the scons debug options. See details at
        # -- https://scons.org/doc/2.4.1/HTML/scons-man.html
        debug_options = (
            ["--debug=explain,prepare,stacktrace", "--tree=all"]
            if util.is_debug()
            else []
        )

        # -- Command to execute: scons -Q apio_cmd flags
        scons_command = (
            ["scons"] + ["-Q", scond_command] + debug_options + variables
        )

        # -- An output filter that manupulates the scons stdout/err lines as
        # -- needed and write them to stdout.
        colors_enabled = Profile.read_color_prefernces()
        scons_filter = SconsFilter(colors_enabled)

        # -- Write the scons parameters to a temp file in the build
        # -- directory. It will be cleaned up as part of 'apio cleanup'.
        # -- At this point, the project is the current directory, even if
        # -- the command used the --project-dir option.
        build_dir = Path("_build")
        os.makedirs(build_dir, exist_ok=True)
        with open(build_dir / "scons.params", "w", encoding="utf8") as f:
            f.write(text_format.MessageToString(scons_params))

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
        secho(f"{half_line} [{status}]{summary_text}{half_line}", err=is_error)

        # -- Return the exit code
        return result.exit_code
