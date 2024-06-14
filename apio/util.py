# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Utility functions"""

import sys
import os
import json
import platform
import subprocess
from threading import Thread
from pathlib import Path
import click
import semantic_version
from serial.tools.list_ports import comports
import requests

# ----------------------------------------
# -- Constants
# ----------------------------------------

# -- Packages names
# -- If you need to create new packages, you should
# -- define first the constants here
# --
OSS_CAD_SUITE = "oss-cad-suite"
GTKWAVE = "gtkwave"

# -- Name of the subfolder to store de executable files
BIN = "bin"

# -- Folder names. They are built from the
# -- packages names
OSS_CAD_SUITE_FOLDER = f"tools-{OSS_CAD_SUITE}"
GTKWAVE_FOLDER = f"tool-{GTKWAVE}"

# -- AVAILABLE PLATFORMS
PLATFORMS = [
    "linux",
    "linux_x86_64",
    "linux_i686",
    "linux_armv7l",
    "linux_aarch64",
    "windows",
    "windows_x86",
    "windows_amd64",
    "darwin",
    "darwin_arm64",
]


class ApioException(Exception):
    """Apio error"""


class AsyncPipe(Thread):
    """DOC: TODO"""

    def __init__(self, outcallback=None):
        Thread.__init__(self)
        self.outcallback = outcallback

        self._fd_read, self._fd_write = os.pipe()
        self._pipe_reader = os.fdopen(self._fd_read)
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
            line = line.strip()
            self._buffer.append(line)
            if self.outcallback:
                self.outcallback(line)
        self._pipe_reader.close()

    def close(self):
        """DOC: TODO"""

        os.close(self._fd_write)
        self.join()


def get_full_path(folder: str) -> Path:
    """Get the full path to the given folder
    Inputs:
      * folder: String with the folder name

    Returns:
      * The full path as a PosixPath() object

    Example: folder="commands"
    Output: PosixPath('/home/obijuan/.../apio/commands')
    """

    # -- Get the full path of this file (util.py)
    # -- Ex: /home/obijuan/.../site-packages/apio/util.py
    current_python_file = Path(__file__)

    # -- The parent folder is the apio root folder
    # -- Ex: /home/obijuan/.../site-packages/apio
    apio_path = current_python_file.parent

    # -- Add the given folder to the path
    new_path = apio_path / folder

    # -- Return the path
    return new_path


def get_systype() -> str:
    """Return a String with the current platform:
    ex. linux_x86_64
    ex. windows_amd64"""

    # -- Get the platform: linux, windows, darwin
    type_ = platform.system().lower()
    platform_str = f"{type_}"

    # -- Get the architecture
    arch = platform.machine().lower()

    # -- Special case for windows
    if type_ == "windows":
        # -- Assume all the windows to be 64-bits
        arch = "amd64"

    # -- Add the architecture, if it exists
    if arch:
        platform_str += f"_{arch}"

    # -- Special case for Darwin: darwin_x86_64 is replace for darwin
    # (for backward compatibility)
    if "darwin_x86_64" in platform_str:
        platform_str = "darwin"

    # -- Return the full platform
    return platform_str


def _get_projconf_option_dir(name: str, default=None):
    """Return the project option with the given name
    These options are place either on environment variables or
    into the /etc/apio.json file in the case of debian distributions

    All the APIO environment variables have the prefix "APIO_"

    Project options:

    * home_dir : APIO home directory
    """

    # -- Get the full name of the environment variable
    _env_name = f"APIO_{name.upper()}"

    # -- Check if the environment variable
    # -- is defined
    if _env_name in os.environ:
        # -- Read the value of the environmental variable
        _env_value = os.getenv(_env_name)

        # -- On window systems the environmental variables can
        # -- include the quotes (""). But not in Linux
        # -- If there are quotes, remove them
        if _env_value.startswith('"') and _env_value.endswith('"'):
            _env_value = _env_value[1:-1]

        return _env_value

    # -- Return the default home_dir
    return default


def get_home_dir() -> Path:
    """Get the APIO Home dir. This is the apio folder where the profle is
    located and the packages installed. The APIO Home dir can be set in the
    APIO_HOME_DIR environment varible or in the /etc/apio.json file (in
    Debian). If not set, the user_HOME/.apio folder is used by default:
    Ej. Linux:  /home/obijuan/.apio
    If the folders does not exist, they are created
    It returns a list with all the folders
    """

    # -- Get the APIO_HOME_DIR env variable
    # -- It returns None if it was not defined
    apio_home_dir_env = _get_projconf_option_dir("home_dir")

    # -- Get the home dir. It is what the APIO_HOME_DIR env variable
    # -- says, or the default folder if None
    if apio_home_dir_env:
        home_dir = Path(apio_home_dir_env)
    else:
        home_dir = Path.home() / ".apio"

    # -- Create the folders if they do not exist
    try:
        home_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        click.secho(f"Error: no usable home directory {home_dir}", fg="red")
        sys.exit(1)

    # Return the home_dir as a Path
    return home_dir


def get_package_dir(pkg_name: str) -> Path:
    """Return the APIO package dir of a given package
    Packages are installed in the following folder:
      * Default: $APIO_HOME_DIR/packages
      * $APIO_PKG_DIR/packages: if the APIO_PKG_DIR env variable is set
      * INPUT:
        - pkg_name: Package name (Ex. 'examples')
      * OUTPUT:
        - The package folder (PosixPath)
           (Ex. '/home/obijuan/.apio/packages/examples'))
        - or None if the packageis not installed
    """

    # -- Get the apio home dir:
    # -- Ex. '/home/obijuan/.apio'
    apio_home_dir = get_home_dir()

    # -- Get the APIO_PKG_DIR env variable
    # -- It returns None if it was not defined
    apio_pkg_dir_env = _get_projconf_option_dir("pkg_dir")

    # -- Get the pkg base dir. It is what the APIO_PKG_DIR env variable
    # -- says, or the default folder if None
    if apio_pkg_dir_env:
        pkg_home_dir = Path(apio_pkg_dir_env)

    # -- Default value
    else:
        pkg_home_dir = apio_home_dir

    # -- Create the package folder
    # -- Ex '/home/obijuan/.apio/packages/tools-oss-cad-suite'
    package_dir = pkg_home_dir / "packages" / pkg_name

    # -- Return the folder if it exists
    if package_dir.exists():
        return package_dir

    # -- No path...
    return None


def call(cmd):
    """Execute the given command from the installed apio packages"""

    # -- Set the PATH environment variable for finding the
    # -- executables on the apio package folders first
    setup_environment()

    # -- Execute the command from the shell
    result = subprocess.call(cmd, shell=True)

    # -- Command not found
    if result == 127:
        message = f"ERROR. Comand not found!: {cmd}"
        click.secho(message, fg="red")

    return result


def setup_environment():
    """Set the environment variables and the system PATH"""

    # --- Get the table with the paths of all the apio packages
    base_dir = get_base_dir()

    # --- Get the table with the paths of all the executables
    # --- of the apio packages
    bin_dir = get_bin_dir_table(base_dir)

    # --- Set the system env. variables
    set_env_variables(base_dir, bin_dir)

    return bin_dir


def set_env_variables(base_dir: dict, bin_dir: dict):
    """Set the environment variables"""

    # -- Get the current system PATH
    path = os.environ["PATH"]

    # -- Add the packages to the path. The first packages added
    # -- have the lowest priority. The latest the highest

    # -- Add the gtkwave to the path if installed,
    # -- but only for windows platforms
    if platform.system() == "Windows":
        # -- Gtkwave package is installed
        if bin_dir[GTKWAVE]:
            path = os.pathsep.join([str(bin_dir[GTKWAVE]), path])

    # -- Add the binary folders of the installed packages
    # -- to the path, except for the OSS_CAD_SUITE package
    for pack in base_dir:
        if base_dir[pack] and pack != OSS_CAD_SUITE:
            path = os.pathsep.join([str(bin_dir[pack]), path])

    # -- Add the OSS_CAD_SUITE package to the path
    # -- if installed (Maximum priority)
    if base_dir[OSS_CAD_SUITE]:
        # -- Get the lib folder (where the shared libraries are located)
        oss_cad_suite_lib = str(base_dir[OSS_CAD_SUITE] / "lib")

        # -- Add the lib folder
        path = os.pathsep.join([oss_cad_suite_lib, path])
        path = os.pathsep.join([str(bin_dir[OSS_CAD_SUITE]), path])

    # Add the virtual python environment to the path
    os.environ["PATH"] = path

    # Add other environment variables

    os.environ["IVL"] = str(base_dir[OSS_CAD_SUITE] / "lib" / "ivl")

    os.environ["ICEBOX"] = str(base_dir[OSS_CAD_SUITE] / "share" / "icebox")

    os.environ["TRELLIS"] = str(base_dir[OSS_CAD_SUITE] / "share" / "trellis")

    os.environ["YOSYS_LIB"] = str(base_dir[OSS_CAD_SUITE] / "share" / "yosys")


def resolve_packages(
    packages: list, installed_packages: list, spec_packages: dict
) -> bool:
    """Check the given packages
    * make sure they all are installed
    * make sure they versions are ok and have no conflicts...
    * INPUTS
      * package: List of package names to check
      * installed_packages: Dictionry with all the apio packages installed
      * spec_packages: Dictionary with the spec version:
        (Ex. {'drivers': '>=1.1.0,<1.2.0'....})

    * OUTPUT:
      * True: All the packages are ok!
      * False: There is an error...
    """

    # --- Get the table with the paths of all the apio packages
    base_dir = get_base_dir()

    # --- Get the table with the paths of all the executables
    # --- of the apio packages
    bin_dir = get_bin_dir_table(base_dir)

    # -- Check packages
    check = True
    for package in packages:
        version = installed_packages.get(package, {}).get("version", "")

        spec_version = spec_packages.get(package, "")

        # -- Get the package binary dir as a PosixPath object
        _bin = bin_dir[package]

        # -- Check this package
        check &= check_package(package, version, spec_version, _bin)

    # -- Load packages
    if check:
        # --- Set the system env. variables
        set_env_variables(base_dir, bin_dir)

    return check


def get_base_dir():
    """Return the table with the local paths of the apio packages
    installed on the system. If the packages is not installed,
    the path is ''
    """

    # -- Create the table:
    # --  Package Name  :  Folder (string)
    base_dir = {
        OSS_CAD_SUITE: get_package_dir(OSS_CAD_SUITE_FOLDER),
        GTKWAVE: get_package_dir(GTKWAVE_FOLDER),
    }

    return base_dir


def get_bin_dir_table(base_dir: dict):
    """Return a table with the package name and the folder were
    the executable files are stored
    * INPUT
      -base_dir: Table with the package base_dir
    """

    if base_dir[GTKWAVE]:
        gtkwave_path = base_dir[GTKWAVE] / BIN
    else:
        gtkwave_path = None

    if base_dir[OSS_CAD_SUITE]:
        oss_cad_suite_path = base_dir[OSS_CAD_SUITE] / BIN
    else:
        oss_cad_suite_path = None

    bin_dir = {OSS_CAD_SUITE: oss_cad_suite_path, GTKWAVE: gtkwave_path}

    return bin_dir


def check_package(
    name: str, version: str, spec_version: str, path: Path
) -> bool:
    """Check if the given package is ok
       (and can be installed without problems)
    * INPUTS:
      - name: Package name
      - version: Package version
      - spec_version: semantic version constraint
      - path: path where the binary files of the package are stored

    * OUTPUT:
      - True: Package
    """

    # Apio package 'gtkwave' only exists for Windows.
    # Linux and MacOS user must install the native GTKWave.
    if name == "gtkwave" and platform.system() != "Windows":
        return True

    # Check package path
    if path and not path.is_dir():
        show_package_path_error(name)
        show_package_install_instructions(name)
        return False

    # Check package version
    if not check_package_version(version, spec_version):
        show_package_version_warning(name, version, spec_version)
        show_package_install_instructions(name)
        return False

    return True


def check_package_version(version: str, spec_version: str) -> bool:
    """Check if a given version satisfy the semantic version constraints
    * INPUTS:
      - version: Package version (Ex. '0.0.9')
      - spec_version: semantic version constraint (Ex. '>=0.0.1')
    * OUTPUT:
      - True: Version ok!
      - False: Version not ok! or incorrect version number
    """

    # -- Build a semantic version object
    spec = semantic_version.SimpleSpec(spec_version)

    # -- Check it!
    try:
        semver = semantic_version.Version(version)

    # -- Incorrect version number
    except ValueError:
        return False

    # -- Check the version (True if the semantic version is satisfied)
    return semver in spec


def show_package_version_warning(name: str, version: str, spec_version: str):
    """Print warning message: semantic version does not match!"""

    message = (
        f"Warning: package '{name}' version {version}\n"
        f"does not match the semantic version {spec_version}"
    )
    click.secho(message, fg="yellow")


def show_package_path_error(name: str):
    """Display an error: package Not installed
    * INPUTs:
      - name: Package name
    """

    message = f"Error: package '{name}' is not installed"
    click.secho(message, fg="red")


def show_package_install_instructions(name: str):
    """Print the package install instructions
    * INPUTs:
      - name: Package name
    """

    click.secho(f"Please run:\n   apio install {name}", fg="yellow")


def get_package_version(name: str, profile: dict) -> str:
    """Get the version of a given package
    * INPUTs:
      - name: Package name
      - profile: Dictrionary with the profile information
    * OUTPUT:
      - The version (Ex. '0.0.9')
    """

    # -- Default version
    version = ""

    # -- Check if the package is intalled
    if name in profile.packages:
        version = profile.packages[name]["version"]

    # -- Return the version
    return version


def get_package_spec_version(name: str, resources: dict) -> str:
    """Get the version restrictions for a given package
    * INPUTs:
      * name: Package name
      * resources: Apio resources object
    * OUTPUT: version restrictions for that package
      Ex. '>=1.1.0,<1.2.0'
    """

    # -- No restrictions by default
    spec_version = ""

    # -- Check that the package is valid
    if name in resources.distribution["packages"]:

        # -- Get the package restrictions
        spec_version = resources.distribution["packages"][name]

    # -- Return the restriction
    return spec_version


def exec_command(*args, **kwargs) -> dict:
    """Execute the given command:

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

    # -- Default value to return after the command execution
    # -- out: string with the command output
    # -- err: string with the command error output
    result = {"out": None, "err": None, "returncode": None}

    # -- Set the default arguments to pass to subprocess.Popen()
    # -- for executing the command
    flags = {
        # -- Catpure the command output
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

            # -- Collect the results
            result["out"], result["err"] = proc.communicate()
            result["returncode"] = proc.returncode

    # -- User has pressed the Ctrl-C for aborting the command
    except KeyboardInterrupt:
        click.secho("Aborted by user", fg="red")
        sys.exit(1)

    # -- The command does not exist!
    except FileNotFoundError:
        click.secho(f"Command not found:\n{args}", fg="red")
        sys.exit(1)

    # -- Close the stdout and stderr pipes
    finally:
        for std in ("stdout", "stderr"):
            if isinstance(flags[std], AsyncPipe):
                flags[std].close()

    # -- Process the output from the stdout and stderr
    # -- if they exist
    for inout in ("out", "err"):

        # -- Construct the Name "stdout" or "stderr"
        std = f"std{inout}"

        # -- Do it only if they have been assigned
        if isinstance(flags[std], AsyncPipe):

            # -- Get the text
            buffer = flags[std].get_buffer()

            # -- Create the full text message (for stdout or stderr)
            # -- result["out"] contains stdout
            # -- result["err"] contains stderr
            result[inout] = "\n".join(buffer)
            result[inout].strip()

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
        req = requests.get("https://pypi.python.org/pypi/apio/json", timeout=5)
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


def check_dir(_dir: Path) -> Path:
    """Check if the given path is a folder. It it does not exists
    the folder is created. If no path is given the current working
    directory is used
      * INPUTS:
        * _dir: The Path to check
      * OUTPUT:
        * The new path (if not given)
    """

    # -- If no path is given, get the current working directory
    if not _dir:
        _dir = Path.cwd()

    # -- Check if the path is a file or a folder
    if _dir.is_file():
        # -- It is a file! Error! Exit!
        click.secho(
            f"Error: project directory is already a file: {_dir}", fg="red"
        )

        sys.exit(1)

    # -- If the folder does not exist....
    if not _dir.exists():
        # -- Warning
        click.secho(f"Warning: The path does not exist: {_dir}", fg="yellow")

        # -- Create the folder
        click.secho(f"Creating folder: {_dir}")
        _dir.mkdir()

    # -- Return the path
    return _dir


# W0703: Catching too general exception Exception (broad-except)
# pylint: disable=W0703
# pylint: disable=W0150
def command(function):
    """Command decorator"""

    def decorate(*args, **kwargs):
        exit_code = 1
        try:
            exit_code = function(*args, **kwargs)

        except Exception as exc:
            if str(exc):
                click.secho("Error: " + str(exc), fg="red")

        return exit_code

    return decorate


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

    # -- Get the output
    out = result["out"]

    try:
        # -- Convert the json string to an object (list)
        meta = json.loads(out)

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


def context_settings():
    """Return a common Click command settings that adds
    the alias -h to --help
    """
    # Per https://click.palletsprojects.com/en/8.1.x/documentation/
    #     #help-parameter-customization
    return {"help_option_names": ["-h", "--help"]}


def safe_click(text, *args, **kwargs):
    """Prints text to the console handling potential Unicode errors,
    forwarding any additional arguments to click.echo. This permits
    avoid the need of setting encode environment variables for utf-8"""

    error_flag = kwargs.pop("err", False)

    try:
        click.echo(text, err=error_flag, *args, **kwargs)
    except UnicodeEncodeError:
        cleaned_text = text.encode("ascii", errors="replace").decode("ascii")
        # if encoding fails, after retry without errors , bad characters are
        # replaced by '?' character, and is better replace for = because is the
        # most common character error
        cleaned_text = "".join([ch if ord(ch) < 128 else "=" for ch in text])
        click.echo(cleaned_text, err=error_flag, *args, **kwargs)
