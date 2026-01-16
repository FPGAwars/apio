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
from contextlib import contextmanager
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, Tuple, List
import subprocess
from threading import Thread
from pathlib import Path
import apio
from apio.utils import env_options
from apio.common.apio_console import cout, cerror
from apio.common.apio_styles import INFO


# ----------------------------------------
# -- Constants
# ----------------------------------------


class ApioException(Exception):
    """Apio error"""


class AsyncPipe(Thread):
    """A class that implements a pipe that calls back on each incoming line
    from an internal thread. Used to process in real time scons output to
    show its progress."""

    def __init__(self, line_callback=None):
        """If line_callback is not None, it is called for each line as
        line_callback(line:str, terminator:str) where line is the line content
        and terminator is one of:
            "\r"   (CR)
            "\n"   (LF)
            ""     (EOF)

        The callback is done from a private Python thread of this pipe so make
        sure to have the proper locking and synchronization as needed.
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

        # -- Append to the lines log buffer.
        self._lines_buffer.append(line)

        # -- Report back if caller passed a callback.
        if self.outcallback:
            self.outcallback(line, terminator)

    def run(self):
        """DOC: TODO"""

        # -- Prepare a buffer for collecting the line chars, excluding
        # -- its line terminator.
        bfr = bytearray()

        # -- We open in binary mode so we have access to the line terminators.
        # -- This is important with progress bars which don't advance to the
        # -- next line but redraw on the same line.
        with os.fdopen(self._fd_read, "rb") as f:
            while True:
                b: Optional[bytearray] = f.read(1)
                assert len(b) <= 1

                # -- Handle end of file
                if not b:
                    if bfr:
                        self._handle_incoming_line(bfr, "")
                    return

                # -- Handle \r terminator
                if b == b"\r":
                    self._handle_incoming_line(bfr, "\r")
                    bfr.clear()
                    continue

                # -- Handle \n terminator
                if b == b"\n":
                    self._handle_incoming_line(bfr, "\n")
                    bfr.clear()
                    continue

                # -- Handle a regular character
                bfr.append(b[0])

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


def exec_command(
    cmd: List[str], stdout: AsyncPipe, stderr: AsyncPipe
) -> CommandResult:
    """Execute the given command using async stdout/stderr..

    NOTE: When running on windows, this function does not support
    privilege elevation, to achieve that, use os.system() instead, as
    done in drivers.py

    INPUTS:
        cmd:    list of command token (strings)
        stdout: the AsyncPipe to use for stdout
        stderr: the AsyncPipe to use for stderr.

    OUTPUT:
        A CommandResult with the command results.
    """

    # -- Sanity check.
    assert isinstance(cmd, list)
    assert isinstance(cmd[0], str)
    assert isinstance(stdout, AsyncPipe)
    assert isinstance(stderr, AsyncPipe)

    # -- Execute the command
    try:
        with subprocess.Popen(
            cmd, stdout=stdout, stderr=stderr, shell=False
        ) as proc:

            # -- Wait for completion.
            out_text, err_text = proc.communicate()

            # -- Get status code.
            exit_code = proc.returncode

            # -- Close the async pipes.
            stdout.close()
            stderr.close()

    # -- User has pressed the Ctrl-C for aborting the command
    except KeyboardInterrupt:
        cerror("Aborted by user")
        # -- NOTE: If using here sys.exit(1), apio requires pressing ctl-c
        # -- twice when running 'apio sim'. This form of exit is more direct
        # -- and harder.
        os._exit(1)

    # -- The command does not exist!
    except FileNotFoundError:
        cerror("Command not found:", cmd)
        sys.exit(1)

    # -- Extract stdout text
    lines = stdout.get_buffer()
    out_text = "\n".join(lines)

    # -- Extract stderr text
    lines = stderr.get_buffer()
    err_text = "\n".join(lines)

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


def get_python_version() -> str:
    """Return a string with the python version"""

    return f"{sys.version_info[0]}.{sys.version_info[1]}"


def get_python_ver_tuple() -> Tuple[int, int, int]:
    """Return a tuple with the python version. e.g. (3, 12, 1)."""
    return sys.version_info[:3]


def plurality(
    obj: Any, singular: str, plural: str = None, include_num: bool = True
) -> str:
    """Returns singular or plural based on the size of the object."""
    # -- Figure out the size of the object
    if isinstance(obj, int):
        n = obj
    else:
        n = len(obj)

    # -- For value of 1 return the singular form.
    if n == 1:
        if include_num:
            return f"{n} {singular}"
        return singular

    # -- For all other values, return the plural form.
    if plural is None:
        plural = singular + "s"

    if include_num:
        return f"{n} {plural}"
    return plural


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


def debug_level() -> int:
    """Returns the current debug level, with 0 as 'off'."""

    # -- We get a fresh value so it can be adjusted dynamically when needed.
    level_str = env_options.get(env_options.APIO_DEBUG, "0")
    try:
        level_int = int(level_str)
    except ValueError:
        cerror(f"APIO_DEBUG value '{level_str}' is not an int.")
        sys.exit(1)

    # -- All done. We don't validate the value, assuming the user knows how
    # -- to use it.
    return level_int


def is_debug(level: int) -> bool:
    """Returns True if apio is in debug mode level 'level'  or higher. Use
    it to enable printing of debug information but not to modify the behavior
    of the code. Also, all apio tests should be performed with debug
    disabled. Important debug information should be at level 1 while
    less important or spammy should be at higher levels."""
    # -- Sanity check. A failure is indicates a programming error.
    assert isinstance(level, int), type(level)
    assert 1 <= level <= 10, level

    return debug_level() >= level


def get_apio_version_tuple() -> Tuple[int]:
    """Returns the version of the apio package as tuple of 3 ints."""
    # -- Apio's version is defined in the __init__.py file of the apio package.
    # -- Using the version from a file in the apio package rather than from
    # -- the pip metadata makes apio more self contained, for example when
    # -- installing with pyinstaller rather than with pip.
    ver: Tuple[int] = apio.APIO_VERSION
    assert len(ver) == 3, ver
    assert isinstance(ver[0], int)
    assert isinstance(ver[1], int)
    assert isinstance(ver[2], int)
    return ver


def get_apio_version_str() -> str:
    """Returns the version of the apio package as a string like "1.22.3"."""
    ver: Tuple[int] = get_apio_version_tuple()
    return f"{ver[0]}.{ver[1]}.{ver[2]}"


def get_apio_release_info() -> str:
    """Returns the release info string."""
    return apio.RELEASE_INFO


def get_apio_version_message() -> str:
    """Returns the string to show on `apio --version`."""
    ver_str = get_apio_version_str()
    release_str = get_apio_release_info() or "no release info"
    return f"Apio CLI version {ver_str} ({release_str})"


def _check_apio_dir(apio_dir: Path, desc: str, env_var: str):
    """Checks the apio home dir or packages dir path for the apio
    requirements."""

    # Sanity check. If this fails, it's a programming error.
    assert isinstance(
        apio_dir, Path
    ), f"Error: {desc} is no a Path: {type(apio_dir)}, {apio_dir}"

    # -- The path should be absolute, see discussion here:
    # -- https://github.com/FPGAwars/apio/issues/522
    if not apio_dir.is_absolute():
        cerror(
            f"Apio {desc} should be an absolute path " f"[{str(apio_dir)}].",
        )
        cout(
            f"You can use the system env var {env_var} to set "
            f"a different apio {desc}.",
            style=INFO,
        )
        sys.exit(1)

    # -- We have problem with spaces and non ascii character above value
    # -- 127, so we allow only ascii characters in the range [33, 127].
    # -- See here https://github.com/FPGAwars/apio/issues/515
    for ch in str(apio_dir):
        if ord(ch) < 33 or ord(ch) > 127:
            cerror(
                f"Unsupported character [{ch}] in apio {desc}: "
                f"[{str(apio_dir)}].",
            )
            cout(
                "Only the ASCII characters in the range 33 to 127 are "
                "allowed. You can use the\n"
                f"system env var '{env_var}' to set a different apio"
                f"{desc}.",
                style=INFO,
            )
            sys.exit(1)


def resolve_home_dir() -> Path:
    """Get the absolute apio home dir. This is the apio folder where the
    profile is located and the packages are installed.
    The apio home dir can be overridden using the APIO_HOME environment
    variable. If not set, the user_home/.apio folder is used by default:
    Ej. Linux:  /home/obijuan/.apio
    If the folders does not exist, they are created
    """

    # -- Get the optional apio home env.
    apio_home_dir_env = env_options.get(env_options.APIO_HOME, default=None)

    # -- If the env vars specified an home dir then use it.
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
    _check_apio_dir(home_dir, "home dir", "APIO_HOME")

    # -- Create the folder if it does not exist
    try:
        home_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        cerror(f"No usable home directory {home_dir}")
        sys.exit(1)

    # Return the home_dir as a Path
    return home_dir


def resolve_packages_dir(apio_home_dir: Path) -> Path:
    """Get the absolute apio packages dir. This is the apio folder where the
    packages are installed. The default apio packages dir can be overridden
    using the APIO_PACKAGES environment variable. If not set,
    the <apio-home>/packages folder is used by default:
    Ej. Linux:  /home/obijuan/.apio/packages
    If the folders does not exist, they are created
    """

    # -- Get the optional apio packages env.
    apio_packages_dir_env = env_options.get(
        env_options.APIO_PACKAGES, default=None
    )

    # -- If the env vars specified an packages dir then use it.
    if apio_packages_dir_env:
        # -- Verify that the env variable contains 'packages' to make sure we
        # -- don't clobber system directories.
        if "packages" not in apio_packages_dir_env:
            cerror(
                "Apio packages dir APIO_PACKAGES should include the "
                "string 'packages'."
            )
            sys.exit(1)
        # -- Expand user home '~' marker, if exists.
        apio_packages_dir_env = os.path.expanduser(apio_packages_dir_env)
        # -- Expand varas such as $HOME or %HOME% on windows.
        apio_packages_dir_env = os.path.expandvars(apio_packages_dir_env)
        # -- Convert string to path.
        packages_dir = Path(apio_packages_dir_env)
    else:
        # -- Else, use the default <home_dir>/packages.
        packages_dir = apio_home_dir / "packages"

    # -- Verify that the home dir meets apio's requirements.
    _check_apio_dir(packages_dir, "packages dir", "APIO_PACKAGES")

    # -- Create the folder if it does not exist
    # try:
    #     packages_dir.mkdir(parents=True, exist_ok=True)
    # except PermissionError:
    #     cerror(f"No usable packages directory {packages_dir}")
    #     sys.exit(1)

    # Return the packages as a Path
    return packages_dir


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
) -> int:
    """A helper for running subprocess.call. Exit if an error."""

    if is_debug(1):
        cout(f"subprocess_call: {cmd}")

    # -- Invoke the command.
    exit_code = subprocess.call(cmd, shell=False)

    if is_debug(1):
        cout(f"subprocess_call: exit code is {exit_code}")

    # -- If ok, return.
    if exit_code == 0:
        return exit_code

    # -- Here when error
    cerror(f"Command failed: {cmd}")
    sys.exit(1)


@contextmanager
def pushd(target_dir: Path):
    """A context manager for temporary execution in a given directory."""
    prev_dir = os.getcwd()
    os.chdir(target_dir)
    try:
        yield
    finally:
        os.chdir(prev_dir)


def is_pyinstaller_app() -> bool:
    """Return true if this is a pyinstaller packaged app.
    Base on https://pyinstaller.org/en/stable/runtime-information.html
    """
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def is_under_vscode_debugger() -> bool:
    """Returns true if running under VSCode debugger."""
    # if os.environ.get("TERM_PROGRAM") == "vscode":
    #     return True
    if os.environ.get("DEBUGPY_RUNNING"):
        return True
    return False
