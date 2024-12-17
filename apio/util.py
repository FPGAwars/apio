# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Misc utility functions and classes."""

import sys
import os
import json
import shutil
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, Tuple, List
import subprocess
from threading import Thread
from pathlib import Path
import click
from serial.tools.list_ports import comports
import requests

# ----------------------------------------
# -- Constants
# ----------------------------------------


class ApioException(Exception):
    """Apio error"""


class AsyncPipe(Thread):
    """DOC: TODO"""

    def __init__(self, outcallback=None):
        Thread.__init__(self)
        self.outcallback = outcallback

        self._fd_read, self._fd_write = os.pipe()
        self._pipe_reader = os.fdopen(self._fd_read, encoding="UTF-8")
        self._buffer = []

        self.start()

    def get_buffer(self):
        """DOC: TODO"""

        return self._buffer

    def fileno(self):
        """DOC: TODO"""

        return self._fd_write

    def run(self):
        """DOC: TODO"""

        for line in iter(self._pipe_reader.readline, ""):
            # We do preserve trailing whitespace and indentation.
            line = line.rstrip()
            self._buffer.append(line)
            if self.outcallback:
                self.outcallback(line)
        self._pipe_reader.close()

    def close(self):
        """DOC: TODO"""

        os.close(self._fd_write)
        self.join()


class TerminalMode(Enum):
    """Represents to two modes of stdout/err."""

    # Output is sent to a terminal. Terminal width is available, and text
    # can have ansi colors.
    TERMINAL = 1
    # Output is sent to a filter or a file. No width and ansi colors should
    # be avoided.
    PIPE = 2


@dataclass(frozen=True)
class TerminalConfig:
    """Contains the stdout/err terminal/pipe configuration."""

    mode: TerminalMode  # TERMINAL or PIPE.
    terminal_width: Optional[int]  # Terminal width. None in PIPE mode.

    def __post_init__(self):
        """Validates initialization."""
        assert isinstance(self.mode, TerminalMode), self
        assert (self.terminal_width is not None) == self.terminal_mode(), self

    def terminal_mode(self) -> bool:
        """True iff in terminal mode."""
        return self.mode == TerminalMode.TERMINAL

    def pipe_mode(self) -> bool:
        """True iff in pipe mode."""
        return self.mode == TerminalMode.PIPE


def get_terminal_config() -> TerminalConfig:
    """Return the terminal configuration of of the current process."""

    # Try to get terminal width, with a fallback default if not a terminal.
    terminal_width, _ = shutil.get_terminal_size(fallback=(999, 999))

    # We got the fallback width so assuming a pipe.
    if terminal_width == 999:
        return TerminalConfig(mode=TerminalMode.PIPE, terminal_width=None)

    # We got an actual terminal width so assuming a terminal.
    return TerminalConfig(
        mode=TerminalMode.TERMINAL, terminal_width=terminal_width
    )


def get_path_in_apio_package(subpath: str) -> Path:
    """Get the full path to the given folder in the apio package.
    Inputs:
      * subdir: String with a relative path within the apio package.
          Use "" for root directory.

    Returns:
      * The absolute path as a PosixPath() object

    Example: folder="commands"
    Output: PosixPath('/home/obijuan/.../apio/commands')
    """

    # -- Get the full path of this file (util.py)
    # -- Ex: /home/obijuan/.../site-packages/apio/util.py
    current_python_file = Path(__file__)

    # -- The parent folder is the apio root folder
    # -- Ex: /home/obijuan/.../site-packages/apio
    path = current_python_file.parent

    # -- Add the given folder to the path. If subpath = "" this
    # -- does nothing, but fails if subpath is None.
    path = path / subpath

    # -- Return the path
    return path


@dataclass(frozen=True)
class CommandResult:
    """Contains the results of a command (subprocess) execution."""

    out_text: Optional[str] = None  # stdout multi-line text.
    err_text: Optional[str] = None  # stderr multi-line text.
    exit_code: Optional[int] = None  # Exit code, 0 = OK.


def exec_command(*args, **kwargs) -> CommandResult:
    """Execute the given command.

    NOTE: When running on windows, this function does not support
    privilege elevation, to achieve that, use os.system() instead.

    INPUTS:
     *args: List with the command and its arguments to execute
     **kwargs: Key arguments when calling subprocess.Popen()
       * stdout
       * stdin
       * shell

    OUTPUT: A dictionary with the following properties:
      * out: String with the output
      * err: String with the error output
      * returncode: Number with the code returned by the command
        * 0: Sucess
        * Another number different from 0: Error!

    Example:  exec_command(['scons', '-Q', '-c', '-f', 'SConstruct'])
    """

    # -- Set the default arguments to pass to subprocess.Popen()
    # -- for executing the command
    flags = {
        # -- Capture the command output
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        # -- Execute it directly, without using the shell
        "shell": False,
    }

    # -- Include the flags given by the user
    # -- It overrides the default flags
    flags.update(kwargs)

    # -- Execute the command!
    try:
        with subprocess.Popen(*args, **flags) as proc:

            # -- Run the command.
            out_text, err_text = proc.communicate()
            exit_code = proc.returncode

            # -- Close the pipes
            for std in ("stdout", "stderr"):
                if isinstance(flags[std], AsyncPipe):
                    flags[std].close()

    # -- User has pressed the Ctrl-C for aborting the command
    except KeyboardInterrupt:
        click.secho("Aborted by user", fg="red")
        sys.exit(1)

    # -- The command does not exist!
    except FileNotFoundError:
        click.secho(f"Command not found:\n{args}", fg="red")
        sys.exit(1)

    # -- If stdout pipe is an AsyncPipe, extract its text.
    pipe = flags["stdout"]
    if isinstance(pipe, AsyncPipe):
        lines = pipe.get_buffer()
        text = "\n".join(lines)
        out_text = text

    # -- If stderr pipe is an AsyncPipe, extract its text.
    pipe = flags["stderr"]
    if isinstance(pipe, AsyncPipe):
        lines = pipe.get_buffer()
        text = "\n".join(lines)
        err_text = text

    # -- All done.
    result = CommandResult(out_text, err_text, exit_code)
    return result


def get_pypi_latest_version() -> str:
    """Get the latest stable version of apio from Pypi
    Internet connection is required
    Returns: A string with the version (Ex: "0.9.0")
      In case of error, it returns None
    """

    # -- Error message common to all exceptions
    error_msg = "Error: could not connect to Pypi\n"

    # -- Read the latest apio version from pypi
    # -- More information: https://warehouse.pypa.io/api-reference/json.html
    try:
        req = requests.get(
            "https://pypi.python.org/pypi/apio/json", timeout=10
        )
        req.raise_for_status()

    # -- Connection error
    except requests.exceptions.ConnectionError as e:
        click.secho(
            f"\n{error_msg}" "Check your internet connection and try again\n",
            fg="red",
        )
        print_exception_developers(e)
        return None

    # -- HTTP Error
    except requests.exceptions.HTTPError as e:
        click.secho(f"\nHTTP ERROR\n{error_msg}", fg="red")
        print_exception_developers(e)
        return None

    # -- Timeout!
    except requests.exceptions.Timeout as e:
        click.secho(f"\nTIMEOUT!\n{error_msg}", fg="red")
        print_exception_developers(e)
        return None

    # -- Another error
    except requests.exceptions.RequestException as e:
        click.secho(f"\nFATAL ERROR!\n{error_msg}", fg="red")
        print_exception_developers(e)
        return None

    # -- Get the version field from the json response
    version = req.json()["info"]["version"]

    return version


def print_exception_developers(e):
    """Print a message for developers, caused by the exception e"""

    click.secho("Info for developers:")
    click.secho(f"{e}\n", fg="yellow")


def get_project_dir(
    _dir: Optional[Path], create_if_missing: bool = False
) -> Path:
    """Check if the given path is a folder. It it does not exists
    and create_if_missing is true, folder is created, otherwise a fatal error.
    If no path is given the current working directory is used.
      * INPUTS:
        * _dir: The Path to check.
      * OUTPUT:
        * The effective path (same if given)
    """
    # -- If no path is given, get the current working directory.
    # -- We Path(".") instead of Path.cwd() to stay with a relative
    # -- (and simple to the user) path.
    if not _dir:
        _dir = Path(".")

    # -- Make sure the folder doesn't exist as a file.
    if _dir.is_file():
        click.secho(
            f"Error: project directory is already a file: {_dir}", fg="red"
        )
        sys.exit(1)

    # -- If the folder does not exist....
    if not _dir.exists():
        if create_if_missing:
            click.secho(
                f"Warning: The path does not exist: {_dir}", fg="yellow"
            )
            click.secho(f"Creating folder: {_dir}")
            _dir.mkdir()
        else:
            click.secho(f"Error: the path does not exist: {_dir}", fg="red")
            sys.exit(1)

    # -- Return the path
    # print(f"*** get_project_dir() {_temp} -> {_dir}")
    return _dir


def get_serial_ports() -> list:
    """Get a list of the serial port devices connected
    * OUTPUT: A list with the devides
         Ex: [{'port': '/dev/ttyACM0',
               'description': 'ttyACM0',
               'hwid': 'USB VID:PID=1D50:6130 LOCATION=1-5:1.0'}]
    """

    # -- Initial empty device list
    result = []

    # -- Use the serial.tools.list_ports module for reading the
    # -- serial ports
    # -- More info:
    # --   https://pyserial.readthedocs.io/en/latest/tools.html
    list_port_info = comports()

    # -- Only the USB serial ports are included
    # -- in the final list
    for port, description, hwid in list_port_info:

        # -- Not a serial port: ignore. Proceed to the
        # -- next device
        if not port:
            continue

        # -- If it has the "VID:PID" string, it is an USB serial port
        if "VID:PID" in hwid:

            # -- Add to the final list
            result.append(
                {"port": port, "description": description, "hwid": hwid}
            )

    # -- Return the list of serial ports
    return result


def get_tinyprog_meta() -> list:
    """Special function for the TinyFPGA board
     Get information directly from the board, just by
     executing the command: "tinyprog --pyserial --meta"

     OUTPUT: It returns a list with the meta-data of all
       the TinyFPGA boards connected
       Ex:
    '[ {"boardmeta": {
          "name": "TinyFPGA BX",
          "fpga": "ice40lp8k-cm81",
          "hver": "1.0.0",
          "uuid": "7d41d659-876b-454a-9a91-51e5f157e80c"
         },
       "bootmeta": {
         "bootloader": "TinyFPGA USB Bootloader",
         "bver": "1.0.1",
         "update": "https://tinyfpga.com/update/tinyfpga-bx",
         "addrmap": {
             "bootloader": "0x000a0-0x28000",
             "userimage": "0x28000-0x50000",
             "userdata": "0x50000-0x100000"
          }\n
        },
        "port": "/dev/ttyACM0"\n
       }
     ]'
    """

    # -- Get the Apio executable folder
    apio_bin_dir = get_bin_dir()

    # -- Construct the command to execute
    _command = apio_bin_dir / "tinyprog"

    # -- Check if the executable exist
    # -- In it does not exist, try with just the
    # -- name: "tinyprog"
    if not _command.exists():
        _command = "tinyprog"

    # -- Execute the command!
    # -- It will return the meta information as a json string
    result = exec_command([_command, "--pyserial", "--meta"])

    # pylint: disable=fixme
    # TODO: Exit with an error if result.exit_code is not zero.

    # -- Convert the json string to an object (list)

    try:
        meta = json.loads(result.out_text)

    except json.decoder.JSONDecodeError as exc:
        click.secho(f"Invalid data provided by {_command}", fg="red")
        click.secho(f"{exc}", fg="red")
        return []

    # -- Return the meta-data
    return meta


# pylint: disable=E1101
# -- E1101: Instance of 'module' has no '__file__' member (no-member)
def get_bin_dir() -> Path:
    """Get the Apio executable Path"""

    # -- Get the apio main module
    main_mod = sys.modules["__main__"]

    # -- Get the full path of the apio executable file
    exec_filename = Path(main_mod.__file__)

    # -- Get its parent directory
    bin_dir = exec_filename.parent

    # -- Special case for Windows + virtualenv
    # In this case the main file is: venv/Scripts/apio.exe/__main__.py!
    # This is not good because venv/Scripts/apio.exe is not a directory
    # So here we go with the workaround:
    if bin_dir.suffix == ".exe":
        return bin_dir.parent

    return bin_dir


def get_python_version() -> str:
    """Return a string with the python version"""

    return f"{sys.version_info[0]}.{sys.version_info[1]}"


def get_python_ver_tuple() -> Tuple[int, int, int]:
    """Return a tuple with the python version. e.g. (3, 12, 1)."""
    return sys.version_info[:3]


def plurality(obj: Any, singular: str, plural: str = None) -> str:
    """Returns singular or plural based on the size of the object."""
    # -- Figure out the size of the object
    if isinstance(obj, int):
        n = obj
    else:
        n = len(obj)

    # -- For value of 1 return the signgular form.
    if n == 1:
        return f"{n} {singular}"

    # -- For all other values, return the plural form.
    if plural is None:
        plural = singular + "s"
    return f"{n} {plural}"


def list_plurality(str_list: List[str], conjunction: str) -> str:
    """Format a list as a human friendly string."""
    # -- This is a programming error. Not a user error.
    assert str_list, "list_plurarlity expect len() >= 1."

    # -- Handle the case of a single item.
    if len(str_list) == 1:
        return str_list[0]

    # -- Handle the case of 2 items.
    if len(str_list) == 2:
        return f"{str_list[0]} {conjunction} {str_list[1]}"

    # -- Handle the case of three or more items.
    return ", ".join(str_list[:-1]) + f", {conjunction} {str_list[-1]}"
