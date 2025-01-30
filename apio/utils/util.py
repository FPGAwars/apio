# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Misc utility functions and classes."""

import sys
import os
import json
import traceback
import importlib.metadata
from functools import wraps
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, Tuple, List
import subprocess
from threading import Thread
from pathlib import Path
from varname import argname
from serial.tools.list_ports import comports
from apio.utils import env_options
from apio.common.apio_console import cout, cerror

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
    path = current_python_file.parent.parent

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
        cerror("Aborted by user")
        sys.exit(1)

    # -- The command does not exist!
    except FileNotFoundError:
        cerror("Command not found:", args)
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


def resolve_project_dir(
    project_dir_arg: Optional[Path],
    *,
    create_if_missing: bool = False,
    must_exist: bool = False,
) -> Path:
    """Check if the given path is a folder. It it does not exists
    and create_if_missing is true, folder is created, otherwise a fatal error.
    If no path is given the current working directory is used.
      * INPUTS:
        * _dir: The Path to check.
      * OUTPUT:
        * The effective path (same if given)
    """
    assert not (create_if_missing and must_exist), "Conflicting flags."

    # -- If no path is given, get the current working directory.
    # -- We use Path(".") instead of Path.cwd() to stay with a relative
    # -- (and simple to the user) path.
    project_dir = project_dir_arg if project_dir_arg else Path(".")

    # -- Make sure the folder doesn't exist as a file.
    if project_dir.is_file():
        cerror(f"Project directory is a file: {project_dir}")
        sys.exit(1)

    # -- If the folder exists we are good
    if project_dir.is_dir():
        return project_dir

    # -- Here when dir doesn't exist. Fatal error if must exist.
    if must_exist:
        cerror(f"Project directory is missing: {str(project_dir)}")
        sys.exit(1)

    # -- Create the directory if requested.
    if create_if_missing:
        cout(f"Creating folder: {project_dir}")
        project_dir.mkdir(parents=True)

    # -- All done
    return project_dir


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

    # -- Construct the command to execute. Since we execute tinyprog from
    # -- the apio packages which add to the path, we can use a simple name.
    command = ["tinyprog", "--pyserial", "--meta"]
    command_str = " ".join(command)

    # -- Execute the command!
    # -- It should return the meta information as a json string
    cout(command_str)
    result = exec_command(command)

    if result.exit_code != 0:
        cout(
            f"Warning: the command '{command_str}' failed with exit code "
            f"{result.exit_code}",
            style="yellow",
        )
        return []

    # -- Convert the json string to an object (list)
    try:
        meta = json.loads(result.out_text)

    except json.decoder.JSONDecodeError as exc:
        cout(
            f"Warning: invalid json data provided by `{command_str}`",
            style="yellow",
        )
        cout(f"{exc}", style="red")
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

    # -- For value of 1 return the singular form.
    if n == 1:
        return f"{n} {singular}"

    # -- For all other values, return the plural form.
    if plural is None:
        plural = singular + "s"
    return f"{n} {plural}"


def list_plurality(str_list: List[str], conjunction: str) -> str:
    """Format a list as a human friendly string."""
    # -- This is a programming error. Not a user error.
    assert str_list, "list_plurality expect len() >= 1."

    # -- Handle the case of a single item.
    if len(str_list) == 1:
        return str_list[0]

    # -- Handle the case of 2 items.
    if len(str_list) == 2:
        return f"{str_list[0]} {conjunction} {str_list[1]}"

    # -- Handle the case of three or more items.
    return ", ".join(str_list[:-1]) + f", {conjunction} {str_list[-1]}"


def is_debug() -> bool:
    """Returns True if apio is in debug mode. Use it to enable printing of
    debug information but not to modify the behavior of the code.
    Also, all apio tests should be performed with debug disabled."""
    return env_options.is_defined("APIO_DEBUG")


def nameof(*_args) -> List[str]:
    """A workaround for the deprecation of varname.nameof(). Returns a list
    of names of the arguments passed to it."""

    # See this discussion for details.
    # github.com/pwwang/python-varname/issues/117#issuecomment-2558351368
    return list(argname("*_args"))


def debug_decorator(func):
    """A decorator for dumping the input and output of a function when
    APIO_DEBUG is defined.  Add it to functions and methods that you want
    to examine with APIO_DEBUG.
    """

    # -- We sample the debug flag upon start.
    debug = is_debug()

    @wraps(func)
    def outer(*args):

        if debug:
            # -- Print the arguments
            cout(
                f"\n>>> Function {os.path.basename(func.__code__.co_filename)}"
                f"/{func.__name__}() BEGIN",
                style="magenta",
            )
            cout("    * Arguments:")
            for arg in args:

                # -- Print all the key,values if it is a dictionary
                if isinstance(arg, dict):
                    cout("        * Dict:")
                    for key, value in arg.items():
                        cout(f"          * {key}: {value}")

                # -- Print the plain argument if it is not a dictionary
                else:
                    cout(f"        * {arg}")
            cout()

        # -- Call the function, dump exceptions, if any.
        try:
            result = func(*args)
        except Exception:
            if debug:
                cout(traceback.format_exc())
            raise

        if debug:
            # -- Print its output
            cout("     Returns: ")

            # -- The return object always is a tuple
            if isinstance(result, tuple):

                # -- Print all the values in the tuple
                for value in result:
                    cout(f"      * {value}")

            # -- But just in case it is not a tuple (because of an error...)
            else:
                cout(f"      * No tuple: {result}")

            cout(
                f"<<< Function {os.path.basename(func.__code__.co_filename)}"
                f"/{func.__name__}() END\n",
                style="magenta",
            )

        return result

    return outer


def get_apio_version() -> str:
    """Returns the version of the apio package."""
    return importlib.metadata.version("apio")


def _check_home_dir(home_dir: Path):
    """Check the path that was specified in APIO_HOME_DIR. Exit with an
    error message if it doesn't comply with apio's requirements.
    """

    # Sanity check. If this fails, it's a programming error.
    assert isinstance(
        home_dir, Path
    ), f"Error: home_dir is no a Path: {type(home_dir)}, {home_dir}"

    # -- The path should be absolute, see discussion here:
    # -- https://github.com/FPGAwars/apio/issues/522
    if not home_dir.is_absolute():
        cerror(
            "Apio home dir should be an absolute path " f"[{str(home_dir)}].",
        )
        cout(
            "You can use the system env var APIO_HOME_DIR to set "
            "a different apio home dir.",
            style="yellow",
        )
        sys.exit(1)

    # -- We have problem with spaces and non ascii character above value
    # -- 127, so we allow only ascii characters in the range [33, 127].
    # -- See here https://github.com/FPGAwars/apio/issues/515
    for ch in str(home_dir):
        if ord(ch) < 33 or ord(ch) > 127:
            cerror(
                f"Unsupported character [{ch}] in apio home dir: "
                f"[{str(home_dir)}].",
            )
            cout(
                "Only the ASCII characters in the range 33 to 127 are "
                "allowed. You can use the\n"
                "system env var 'APIO_HOME_DIR' to set a different apio"
                "home dir.",
                style="yellow",
            )
            sys.exit(1)


def resolve_home_dir() -> Path:
    """Get the absolute apio home dir. This is the apio folder where the
    profile is located and the packages are installed.
    The apio home dir can be overridden using the APIO_HOME_DIR environment
    variable or in the /etc/apio.json file (in
    Debian). If not set, the user_home/.apio folder is used by default:
    Ej. Linux:  /home/obijuan/.apio
    If the folders does not exist, they are created
    """

    # -- Get the APIO_HOME_DIR env variable
    # -- It returns None if it was not defined
    apio_home_dir_env = env_options.get(
        env_options.APIO_HOME_DIR, default=None
    )

    # -- Get the home dir. It is what the APIO_HOME_DIR env variable
    # -- says, or the default folder if None
    if apio_home_dir_env:
        # -- Expand user home '~' marker, if exists.
        apio_home_dir_env = os.path.expanduser(apio_home_dir_env)
        # -- Expand varas such as $HOME or %HOME% on windows.
        apio_home_dir_env = os.path.expandvars(apio_home_dir_env)
        # -- Convert string to path.
        home_dir = Path(apio_home_dir_env)
    else:
        home_dir = Path.home() / ".apio"

    # -- Verify that the home dir meets apio's requirements.
    _check_home_dir(home_dir)

    # -- Create the folder if it does not exist
    try:
        home_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        cerror(f"No usable home directory {home_dir}")
        sys.exit(1)

    # Return the home_dir as a Path
    return home_dir


def split(
    s: str,
    separator: str,
    strip: bool = False,
    keep_empty: bool = True,
) -> str:
    """Split a string into parts."""
    # -- A workaround for python's "".split(",") returning [''].
    s = s.split(separator) if s else []

    # -- Strip the elements if requested.
    if strip:
        s = [x.strip() for x in s]

    # -- Remove empty elements if requested.
    if not keep_empty:
        s = [x for x in s if x]

    # --All done.
    return s


def fpga_arch_sort_key(fpga_arch: str) -> Any:
    """Given an fpga arch name such as 'ice40', return a sort key
    got force our preferred order of sorting by architecture. Used in
    reports such as examples, fpgas, and boards."""

    # -- The preferred order of architectures, Add more if adding new
    # -- architectures.
    archs = ["ice40", "ecp5", "gowin"]

    # -- Primary key with preferred architecture first and  in the
    # -- preferred order.
    primary_key = archs.index(fpga_arch) if fpga_arch in archs else len(archs)

    # -- Construct the key, unknown architectures list at the end by
    # -- lexicographic order.
    return (primary_key, fpga_arch)
