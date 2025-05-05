"""DOC: TODO"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

import re
import sys
from typing import Optional, List
from apio.common.apio_console import cout, cerror, cwarning
from apio.common.apio_styles import INFO
from apio.utils import util, pkg_util
from apio.managers.system import System, FtdiDevice
from apio.apio_context import ApioContext


def construct_programmer_cmd(
    apio_ctx: ApioContext,
    serial_port_arg: Optional[str],
    ftdi_idx_arg: Optional[int],
    sram: bool,
) -> str:
    """Get the command line (string) to execute for programming
    the FPGA (programmer executable + arguments)

    * INPUT
        * apio_ctx: ApioContext of this apio invocation.
        * serial_port: Optional, serial port name
        * ftdi_idx: Optional, restrict to ftdi device with given index
        * sram: Perform SRAM programming

    * OUTPUT: A string with the command+args to execute and a $SOURCE
        placeholder for the bitstream file name.
    """

    # -- Get the board info.
    board = apio_ctx.project["board"]
    assert board
    board_info = apio_ctx.boards[board]

    # -- Serialize programmer command
    # -- Get a string with the command line to execute
    # -- BUT! it is a TEMPLATE string, with some parameters
    # -- that needs to be set!
    # --   * "${VID}" (optional): USB vendor id
    # --   * "${PID}" (optional): USB Product id
    # --   * "${FTDI_IDX}" (optional): FTDI idx (e.g. 0, 1, 2...)
    # --   * "${SERIAL_PORT}" (optional): Serial port name
    programmer = _construct_programmer_cmd_template(apio_ctx, board_info, sram)
    if util.is_debug():
        cout(f"Programmer template: [{programmer}]")
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
    # -- Ex. "${FTDI_IDX}" --> "0"
    if "${FTDI_IDX}" in programmer:
        # -- Inform the user we are accessing the programmer
        # -- to give context for ftdi failures.
        # -- We force an early env setting message to have
        # -- the programmer message closer to the error message.
        pkg_util.set_env_for_packages(apio_ctx)
        cout("Querying programmer parameters.")

        # -- Check that the board is connected
        # -- If not, an exception is raised
        _check_usb(apio_ctx, board, board_info)

        # -- Get the FTDI index of the connected board
        device_ftdi_idx = _get_ftdi_idx(
            apio_ctx, board, board_info, ftdi_idx_arg
        )

        if util.is_debug():
            cout(f"FTDI index: {device_ftdi_idx}")

        # -- Place the value in the command string
        programmer = programmer.replace("${FTDI_IDX}", str(device_ftdi_idx))

    # -- NOTE: We use 'is not None' since 0 is a valid FTDI index.
    elif ftdi_idx_arg is not None:
        # -- The user has specified a FTDI index but the
        # -- programmer does not use it. Ignore the value.
        cwarning(
            f"FTDI index {ftdi_idx_arg} ignored for "
            f"programmer {board_info['programmer']['type']}"
        )

    # Replace Serial port
    # -- The board uses a Serial port for uploading the circuit
    if "${SERIAL_PORT}" in programmer:
        # -- Inform the user we are accessing the programmer
        # -- to give context for ftdi failures.
        # -- We force an early env setting message to have
        # -- the programmer message closer to the error message.
        pkg_util.set_env_for_packages(apio_ctx)
        cout("Querying serial port parameters.")

        # -- Check that the board is connected
        _check_usb(apio_ctx, board, board_info)

        # -- Get the serial port
        device = _get_serial_port(board, board_info, serial_port_arg)

        # -- Place the value in the command string
        programmer = programmer.replace("${SERIAL_PORT}", device)

    elif serial_port_arg:
        # -- The user has specified a serial port but the
        # -- programmer does not use it. Ignore the value.
        cwarning(
            f"Serial port {serial_port_arg} ignored for "
            f"programmer {board_info['programmer']['type']}"
        )

    # -- Return the Command to execute for uploading the circuit
    # -- to the given board. Scons will replace $SOURCE with the
    # -- bitstream file name before executing the command.
    assert "$SOURCE" in programmer, programmer
    return programmer


def _construct_programmer_cmd_template(
    apio_ctx: ApioContext, board_info: dict, sram: bool
) -> str:
    """
    * INPUT:
        * board_info: Dictionary with board info from boards.jsonc.
    * OUTPUT: It returns a template string with the command line
        to execute for uploading the circuit. It has the following
        parameters (in the string):
        * "${VID}" (optional): USB vendor id
        * "${PID}" (optional): USB Product id
        * "${FTDI_IDX}" (optional): FTDI idx
        * "${SERIAL_PORT}" (optional): Serial port name

        Example of output strings:
        "'tinyprog --pyserial -c ${SERIAL_PORT} --program $SOURCE'"
        "'iceprog -d i:0x${VID}:0x${PID}:${FTDI_IDX} $SOURCE'"
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
    programmer_info = apio_ctx.programmers[prog_type]

    # -- Get the command (without arguments) to execute
    # -- for programming the current board
    # -- Ex. "tinyprog"
    # -- Ex. "iceprog"
    programmer_cmd = programmer_info["command"]

    # -- Let's add the arguments for executing the programmer
    if programmer_info.get("args"):
        programmer_cmd += f" {programmer_info['args']}"

    # -- Mark the expected location of the bitstream file name, before
    # -- we appened any arg to the command. Some programmers such as
    # -- dfu-util require it immediatly after the "args" string.
    programmer_cmd += " $SOURCE"

    # -- Some tools need extra arguments
    # -- (like dfu-util for example)
    if prog_info.get("extra_args"):
        programmer_cmd += f" {prog_info['extra_args']}"

    # -- Special case for specific programmers

    # -- Enable SRAM programming for the iceprog* programmer only.
    if sram:
        # Only for iceprog programmer
        if programmer_cmd.startswith("iceprog"):
            programmer_cmd += " -S"
        else:
            # -- Programmer not supported
            cerror(
                "The --sram flag is not available for the "
                f"{prog_type} programmer."
            )
            sys.exit(1)

    return programmer_cmd


def _check_usb(apio_ctx: ApioContext, board: str, board_info: dict) -> None:
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
        cerror("Missing board configuration: usb")
        sys.exit(1)

    # -- Get the vid and pid from the configuration
    # -- Ex. {'vid': '0403', 'pid':'6010'}
    usb_data = board_info["usb"]

    # -- Create a string with vid, pid in the format "vid:pid"
    hwid = f"{usb_data['vid']}:{usb_data['pid']}"

    # -- Get the list of the connected USB devices
    # -- (execute the command "lsusb" from the apio System module)
    system = System(apio_ctx)
    connected_devices = system.get_usb_devices()

    if util.is_debug():
        cout(f"usb devices: {connected_devices}")

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
        cerror("Board " + board + " not connected")

        # -- Special case! TinyFPGA board
        # -- Maybe the board is NOT detected because
        # -- the user has not press the reset button and the bootloader
        # -- is not active
        if "tinyprog" in board_info:
            cout(
                "Activate bootloader by pressing the reset button",
                style=INFO,
            )
        sys.exit(1)


def _get_serial_port(
    board: str, borad_info: dict, ext_serial_port: str
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
    device = _check_serial(board, borad_info, ext_serial_port)

    # -- Board not connected
    if not device:
        cerror("Board " + board + " not connected")
        sys.exit(1)

    # -- Board connected. Return the serial port detected
    return device


def _check_serial(board: str, board_info: dict, ext_serial_port: str) -> str:
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
        cerror("Missing board configuration: usb")
        sys.exit(1)

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

    if util.is_debug():
        cout(f"serial ports: {serial_ports}")

    # -- If no serial ports detected, exit with an error.
    if not serial_ports:
        cerror("Board " + board + " not available")
        sys.exit(1)

    # -- Match the discovered serial ports
    for serial_port_data in serial_ports:

        # -- Get the port name of the detected board
        port = serial_port_data["port"]

        # If the --device options is set but it doesn't match
        # the detected port, skip the port.
        if ext_serial_port and ext_serial_port != port:
            continue

        # -- Check if the TinyFPGA board is connected
        connected = _check_tinyprog(board_info, port)

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


def _get_ftdi_idx(
    apio_ctx: ApioContext, board: str, board_info, ftdi_idx_arg: Optional[int]
) -> int:
    """Get the FTDI index of the detected board

    * INPUT:
        * board: Board name (string)
        * board_info: Dictionary with board info from boards.jsonc.
        * ftdi_idx_arg: FTDI index given by the user (optional)

    * OUTPUT: It return the FTDI index.

        It raises an exception if no FTDI device is connected
    """

    # -- Search device description matching.
    ftdi_idx: Optional[int] = _check_ftdi(
        apio_ctx, board, board_info, ftdi_idx_arg
    )

    # -- No matching FTDI board connected
    if ftdi_idx is None:
        cerror("Board " + board + " not found")
        cout(
            "Run 'apio drivers list ftdi' to see the available FTDI devices",
            style=INFO,
        )

        sys.exit(1)

    # -- Return the FTDI index, e.g. 0.
    return ftdi_idx


def _check_ftdi(
    apio_ctx: ApioContext,
    board: str,
    board_info: dict,
    ftdi_idx_arg: Optional[int],
) -> Optional[int]:
    """Check if the given ftdi board is connected or not to the computer
        and return its FTDI index

    * INPUT:
        * board: Board name (string)
        * board_info: Dictionary with board info from boards.jsonc.
        * ftdi_idx_arg: FTDI index given by the user (optional)

    * OUTPUT: The FTDI device index or None if no board is found.
    """

    # -- Check that the given board has the property "ftdi"
    # -- If not, it is an error. Raise an exception
    if "ftdi" not in board_info:
        cerror("Missing board configuration: ftdi")
        sys.exit(1)

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
    system = System(apio_ctx)
    connected_devices: List[FtdiDevice] = system.get_ftdi_devices()

    # -- No FTDI devices detected --> Error!
    if not connected_devices:
        cerror("Board " + board + " not available")
        sys.exit(1)

    # -- Check if the given board is connected
    # -- and if so, return its FTDI index
    for ftdi_device in connected_devices:

        # -- Get the FTDI index
        # -- Ex: '0'
        ftdi_idx: int = ftdi_device.ftdi_idx

        # If the --ftdi-idx options is set, we consider only the device
        # with given index in the lsftdi output. This is useful in case
        # multiple compatible boards are connected to the host computer.
        if ftdi_idx_arg is not None and ftdi_idx_arg != ftdi_idx:
            continue

        # If matches the description pattern
        # return the index for the FTDI device.
        if re.match(desc_pattern, ftdi_device.description):
            return ftdi_idx

    # -- No FTDI board found
    return None
