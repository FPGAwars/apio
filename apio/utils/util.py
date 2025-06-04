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
import traceback
from functools import wraps
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, Tuple, List
import subprocess
from threading import Thread
from pathlib import Path
import apio
from apio.utils import env_options
from apio.common.apio_console import cout, cerror
from apio.common.apio_styles import INFO, ERROR, EMPH3


# ----------------------------------------
# -- Constants
# ----------------------------------------


class ApioException(Exception):
    """Apio error"""


class AsyncPipe(Thread):
    """DOC: TODO"""

    def __init__(self, line_callback=None):
        """If line_callback is not None, it is called for each line as
        line_callback(line:str, terminator:str) where line is the line content
        and terminator is one of:
            "\r"   (CR)
            "\n"   (LF)
            "\r\r" (CR/LF)
            ""     (EOF)
        """

        Thread.__init__(self)
        self.outcallback = line_callback

        self._fd_read, self._fd_write = os.pipe()

        # -- A list of lines received so far.
        self._lines_buffer = []

        self.start()

    def get_buffer(self):
        """DOC: TODO"""

        return self._lines_buffer

    def fileno(self):
        """DOC: TODO"""

        return self._fd_write

    def _handle_incoming_line(self, bfr: bytearray, terminator: str):
        """Handle a new incoming line.
        Bfr is a bytes with the line's content, possibly empty.
        See __init__ for the description of terminator.
        """

        # -- Convert the line's bytes to a string. Replace invalid utf-8
        # -- chars with "�"
        line = bfr.decode("utf-8", errors="replace")

        # -- Trim trailing space, leaving leading space to preserve
        # -- indentation.
        # line = line.rstrip()

        # -- Append to the lines buffer.
        self._lines_buffer.append(line)

        # -- Report back if caller passed a callback.
        if self.outcallback:
            # self.outcallback(line, terminator)
            self.outcallback(line, terminator)

    def run(self):
        """DOC: TODO"""
        # -- Indicate if a "\r" is pending for reporting.
        pending_cr = False

        # -- Collects the line's chars, excluding the terminators.
        bfr = bytearray()

        # -- We open in binary mode so we have access to the line terminators.
        # -- This is important with progress bars which don't advance to the
        # -- next line but redraw on the same line.
        with os.fdopen(self._fd_read, "rb") as f:
            while True:
                b: Optional[bytearray] = f.read(1)
                assert len(b) <= 1

                if not b:
                    # -- Handle EOF
                    if bfr or pending_cr:
                        # -- Report if we have anything pending.
                        terminator = "\r" if pending_cr else ""
                        self._handle_incoming_line(bfr, terminator)
                    # -- All done, exit
                    break

                if b == b"\r":
                    # -- Handle "\r"
                    if not pending_cr:
                        # -- Save the "\r" and continue.
                        pending_cr = True
                        continue
                    # -- We got two consecutive "\r", report the first one.
                    self._handle_incoming_line(bfr, "\r")
                    # -- Clear the line buffer, keep pending_cr True.
                    bfr.clear()
                    continue

                if b == b"\n":
                    # -- Handle "\n". We always report, with or without a
                    # -- pending "\r"
                    terminator = "\r\n" if pending_cr else "\n"
                    self._handle_incoming_line(bfr, terminator)
                    # -- Clear the line.
                    pending_cr = False
                    bfr.clear()
                    continue

                # -- Else, handle a regular char.
                if pending_cr:
                    # -- We got a regular char after a "\r", with report
                    # -- the line with "\r" terminator and clear the line.
                    self._handle_incoming_line(bfr, "\r")
                    pending_cr = False
                    bfr.clear()
                # -- Append the regular char to the buffer.
                bfr.append(b[0])

        # -- All done.

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
        # NOTE: If using here sys.exit(1), apio requires pressing ctl-c twice
        # when running 'apio sim'. This form of exist is more direct and
        # 'hard'.
        os._exit(1)

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


def user_directory_or_cwd(
    dir_arg: Optional[Path],
    *,
    description: str,
    must_exist: bool = False,
    create_if_missing=False,
) -> Path:
    """Condition a directory arg with current directory as default. If dir_arg
    is specified, it is return after validation, else cwd "." is returned.
    Description is directory function to include in error messages, e.g.
    "Project" or "Destination".
    """

    assert not (create_if_missing and must_exist), "Conflicting flags."

    # -- Case 1: User provided dir path.
    if dir_arg:
        project_dir = dir_arg

        # -- If exists, it must be a dir.
        if project_dir.exists() and not project_dir.is_dir():
            cerror(f"{description} directory is a file: {project_dir}")
            sys.exit(1)

        # -- If required, it must exist.
        if must_exist and not project_dir.exists():
            cerror(f"{description} directory is missing: {str(project_dir)}")
            sys.exit(1)

        # -- If requested, create
        if create_if_missing and not project_dir.exists():
            cout(f"Creating folder: {project_dir}")
            project_dir.mkdir(parents=True)

        # -- All done.
        return project_dir

    # -- Case 2: Using current directory.
    # -- We prefer the relative path "." over the absolute path Path.cwd().
    return Path(".")


def get_bin_dir() -> Path:
    """Get the Apio executable Path"""

    # E1101: Instance of 'module' has no '__file__' member (no-member)
    # pylint: disable=no-member

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
                style=EMPH3,
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
                style=EMPH3,
            )

        return result

    return outer


def get_apio_version() -> str:
    """Returns the version of the apio package."""
    # -- Apio's version is defined in the __init__.py file of the apio package.
    # -- Using the version from a file in the apio package rather than from
    # -- the pip metadata makes apio more self contained, for example when
    # -- installing with pyinstaller rather than with pip.
    ver: Tuple[int] = apio.VERSION
    assert len(ver) == 3, ver
    # -- Format the tuple of three ints as a string such as "0.9.83"
    return f"{ver[0]}.{ver[1]}.{ver[2]}"


def _check_home_dir(home_dir: Path):
    """Check the path that was specified in APIO_HOME. Exit with an
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
            "You can use the system env var APIO_HOME to set "
            "a different apio home dir.",
            style=INFO,
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
                "system env var 'APIO_HOME' to set a different apio"
                "home dir.",
                style=INFO,
            )
            sys.exit(1)


def resolve_home_dir() -> Path:
    """Get the absolute apio home dir. This is the apio folder where the
    profile is located and the packages are installed.
    The apio home dir can be overridden using the APIO_HOME environment
    variable or in the /etc/apio.json file (in
    Debian). If not set, the user_home/.apio folder is used by default:
    Ej. Linux:  /home/obijuan/.apio
    If the folders does not exist, they are created
    """

    # -- Try the env vars, by decreasing order of importance.
    for var in [
        env_options.APIO_HOME,
        env_options.APIO_HOME_DIR,
    ]:
        apio_home_dir_env = env_options.get(var, default=None)
        if apio_home_dir_env:
            break

    # -- If the env vars specified an home dir then process it.
    if apio_home_dir_env:
        # -- Expand user home '~' marker, if exists.
        apio_home_dir_env = os.path.expanduser(apio_home_dir_env)
        # -- Expand varas such as $HOME or %HOME% on windows.
        apio_home_dir_env = os.path.expandvars(apio_home_dir_env)
        # -- Convert string to path.
        home_dir = Path(apio_home_dir_env)
    else:
        # -- Else, use the default home dir ~/.apio.
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


def subprocess_call(
    cmd: List[str],
    shell: bool = False,
    exit_on_error: bool = False,
    failure_msg: str = None,
    failure_msg_style: str = ERROR,
) -> int:
    """A helper for running subprocess.call."""

    if is_debug():
        cout(f"subprocess_call: {cmd}")

    # -- Invoke the command.
    exit_code = subprocess.call(cmd, shell=shell)

    if is_debug():
        cout(f"subprocess_call: exit code is {exit_code}")

    # -- If ok, return.
    if exit_code == 0:
        return exit_code

    # -- Print the messages
    cerror(f"Command failed: {cmd}")
    if failure_msg:
        cout(failure_msg, style=failure_msg_style)

    # -- Exit if requested.
    if exit_on_error:
        sys.exit(1)

    # -- Return with the error code.
    return exit_code
