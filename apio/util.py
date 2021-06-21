"""DOC: TODO"""
# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2

import sys
import os
import re
import json
import locale
import platform
import subprocess
from threading import Thread
from os.path import expanduser, isdir, isfile, join, dirname, exists, normpath

import jwt
import click
import semantic_version
from serial.tools.list_ports import comports
import requests

from apio import LOAD_CONFIG_DATA


requests.packages.urllib3.disable_warnings()


# Python3 compat
if sys.version_info > (3, 0):
    unicode = str


class ApioException(Exception):
    """DOC: TODO"""

    MESSAGE = None

    def __str__(self):  # pragma: no cover
        if self.MESSAGE:
            return self.MESSAGE.format(*self.args)

        return Exception.__str__(self)


class AsyncPipe(Thread):  # pragma: no cover
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


def get_systype():
    """DOC: TODO"""

    type_ = platform.system().lower()
    arch = platform.machine().lower()
    if type_ == "windows":
        arch = "amd64" if platform.architecture()[0] == "64bit" else "x86"
    return "%s_%s" % (type_, arch) if arch else type_


try:
    codepage = locale.getdefaultlocale()[1]
    if "darwin" in get_systype():
        UTF = True
    else:
        UTF = codepage.lower().find("utf") >= 0
except Exception:
    # Incorrect locale implementation, assume the worst
    UTF = False


def unicoder(string):
    """Make sure a Unicode string is returned"""
    if isinstance(string, unicode):
        return string

    if isinstance(string, str):
        return decoder(string)

    return unicode(decoder(string))


def decoder(string):
    """DOC: TODO"""

    if UTF:
        try:
            return string.decode("utf-8")
        except Exception:
            return string.decode(codepage)
    return string.decode(codepage)


def safe_join(*paths):
    """Join paths in a Unicode-safe way"""
    try:
        return join(*paths)
    except UnicodeDecodeError:
        npaths = ()
        for path in paths:
            npaths += (unicoder(path),)
        return join(*npaths)


def _get_config_data():
    _config_data = None
    if LOAD_CONFIG_DATA:
        filepath = safe_join(os.sep, "etc", "apio.json")
        if isfile(filepath):
            with open(filepath, "r") as file:
                # Load the JSON file
                _config_data = json.loads(file.read())
    return _config_data


config_data = _get_config_data()


def _get_projconf_option_dir(name, default=None):
    _env_name = "APIO_%s" % name.upper()
    if _env_name in os.environ:
        return os.getenv(_env_name)
    if config_data and _env_name in config_data.keys():
        return config_data.get(_env_name)
    return default


def get_home_dir():
    """DOC: TODO"""

    home_dir = _get_projconf_option_dir("home_dir", "~/.apio")
    home_dir = re.sub(r"\~", expanduser("~").replace("\\", "/"), home_dir)

    paths = home_dir.split(os.pathsep)
    path = _check_writable(paths)
    if not path:
        path = _create_path(paths)
        if not path:
            click.secho("Error: no usable home directory " + path, fg="red")
            sys.exit(1)
    return path


def _check_writable(paths):
    ret = ""
    for path in paths:
        if isdir(path):
            if os.access(path, os.W_OK):
                # Path is writable
                ret = path
                break
            click.secho("Warning: can't write in path " + path, fg="yellow")
    return ret


def _create_path(paths):
    ret = ""
    for path in paths:
        if not isdir(path):
            try:
                os.makedirs(path)
                ret = path
                break
            except OSError as ioex:
                if ioex.errno == 13:
                    click.secho("Warning: can't create " + path, fg="yellow")
    return ret


def get_package_dir(pkg_name):
    """DOC: TODO"""

    home_dir = _get_projconf_option_dir("pkg_dir", "")
    if not home_dir:
        home_dir = _get_projconf_option_dir("home_dir", "~/.apio")
    home_dir = re.sub(r"\~", expanduser("~").replace("\\", "/"), home_dir)

    paths = home_dir.split(os.pathsep)
    for path in paths:
        package_dir = safe_join(path, "packages", pkg_name)
        if isdir(package_dir):
            return package_dir

    return ""


def get_project_dir():
    """DOC: TODO"""

    return os.getcwd()


def call(cmd):
    """DOC: TODO"""

    setup_environment()
    return subprocess.call(cmd, shell=True)


def setup_environment():
    """DOC: TODO"""

    base_dir = {
        "scons": get_package_dir("tool-scons"),
        "system": get_package_dir("tools-system"),
        "yosys": get_package_dir("toolchain-yosys"),
        "ice40": get_package_dir("toolchain-ice40"),
        "ecp5": get_package_dir("toolchain-ecp5"),
        "iverilog": get_package_dir("toolchain-iverilog"),
        "verilator": get_package_dir("toolchain-verilator"),
        "gtkwave": get_package_dir("tool-gtkwave"),
        "fujprog": get_package_dir("toolchain-fujprog"),
        "icesprog": get_package_dir("toolchain-icesprog"),
        "dfu": get_package_dir("toolchain-dfu"),
        "openfpgaloader": get_package_dir("toolchain-ecp5"),
    }

    bin_dir = {
        "scons": safe_join(base_dir.get("scons"), "script"),
        "system": safe_join(base_dir.get("system"), "bin"),
        "yosys": safe_join(base_dir.get("yosys"), "bin"),
        "ice40": safe_join(base_dir.get("ice40"), "bin"),
        "ecp5": safe_join(base_dir.get("ecp5"), "bin"),
        "iverilog": safe_join(base_dir.get("iverilog"), "bin"),
        "verilator": safe_join(base_dir.get("verilator"), "bin"),
        "gtkwave": safe_join(base_dir.get("gtkwave"), "bin"),
        "fujprog": safe_join(base_dir.get("fujprog"), "bin"),
        "icesprog": safe_join(base_dir.get("icesprog"), "bin"),
        "dfu": safe_join(base_dir.get("dfu"), "bin"),
        "openfpgaloader": safe_join(base_dir.get("openfpgaloader"), "bin"),
    }

    # Give the priority to the python packages installed with apio
    os.environ["PATH"] = os.pathsep.join([get_bin_dir(), os.environ["PATH"]])

    # Give the priority to the packages installed by apio
    os.environ["PATH"] = os.pathsep.join(
        [
            bin_dir.get("yosys"),
            bin_dir.get("ice40"),
            bin_dir.get("ecp5"),
            bin_dir.get("iverilog"),
            bin_dir.get("verilator"),
            bin_dir.get("fujprog"),
            bin_dir.get("icesprog"),
            bin_dir.get("dfu"),
            bin_dir.get("openfpgaloader"),
            os.environ["PATH"],
        ]
    )

    if platform.system() == "Windows":
        os.environ["PATH"] = os.pathsep.join(
            [bin_dir.get("gtkwave"), os.environ["PATH"]]
        )

    # Add environment variables
    if not config_data:  # /etc/apio.json file does not exist
        os.environ["IVL"] = safe_join(base_dir.get("iverilog"), "lib", "ivl")
    os.environ["ICEBOX"] = safe_join(base_dir.get("ice40"), "share", "icebox")
    os.environ["TRELLIS"] = safe_join(base_dir.get("ecp5"), "share", "trellis")
    os.environ["YOSYS_LIB"] = safe_join(
        base_dir.get("yosys"), "share", "yosys"
    )

    return bin_dir


def resolve_packages(packages, installed_packages, spec_packages):
    """DOC: TODO"""

    base_dir = {
        "scons": get_package_dir("tool-scons"),
        "system": get_package_dir("tools-system"),
        "yosys": get_package_dir("toolchain-yosys"),
        "ice40": get_package_dir("toolchain-ice40"),
        "ecp5": get_package_dir("toolchain-ecp5"),
        "iverilog": get_package_dir("toolchain-iverilog"),
        "verilator": get_package_dir("toolchain-verilator"),
        "gtkwave": get_package_dir("tool-gtkwave"),
        "fujprog": get_package_dir("toolchain-fujprog"),
        "icesprog": get_package_dir("toolchain-icesprog"),
        "dfu": get_package_dir("toolchain-dfu"),
        "openfpgaloader": get_package_dir("toolchain-ecp5"),
    }

    bin_dir = {
        "scons": safe_join(base_dir.get("scons"), "script"),
        "system": safe_join(base_dir.get("system"), "bin"),
        "yosys": safe_join(base_dir.get("yosys"), "bin"),
        "ice40": safe_join(base_dir.get("ice40"), "bin"),
        "ecp5": safe_join(base_dir.get("ecp5"), "bin"),
        "iverilog": safe_join(base_dir.get("iverilog"), "bin"),
        "verilator": safe_join(base_dir.get("verilator"), "bin"),
        "gtkwave": safe_join(base_dir.get("gtkwave"), "bin"),
        "fujprog": safe_join(base_dir.get("fujprog"), "bin"),
        "icesprog": safe_join(base_dir.get("icesprog"), "bin"),
        "dfu": safe_join(base_dir.get("dfu"), "bin"),
        "openfpgaloader": safe_join(base_dir.get("openfpgaloader"), "bin"),
    }

    # -- Check packages
    check = True
    for package in packages:
        version = installed_packages.get(package, {}).get("version", "")
        spec_version = spec_packages.get(package, "")
        check &= check_package(
            package, version, spec_version, bin_dir.get(package)
        )

    # -- Load packages
    if check:

        # Give the priority to the python packages installed with apio
        os.environ["PATH"] = os.pathsep.join(
            [get_bin_dir(), os.environ["PATH"]]
        )

        # Give the priority to the packages installed by apio
        os.environ["PATH"] = os.pathsep.join(
            [
                bin_dir.get("yosys"),
                bin_dir.get("ice40"),
                bin_dir.get("ecp5"),
                bin_dir.get("iverilog"),
                bin_dir.get("verilator"),
                bin_dir.get("fujprog"),
                bin_dir.get("icesprog"),
                bin_dir.get("dfu"),
                bin_dir.get("openfpgaloader"),
                os.environ["PATH"],
            ]
        )

        if platform.system() == "Windows":
            os.environ["PATH"] = os.pathsep.join(
                [bin_dir.get("gtkwave"), os.environ["PATH"]]
            )

        # Add environment variables
        if not config_data:  # /etc/apio.json file does not exist
            os.environ["IVL"] = safe_join(
                base_dir.get("iverilog"), "lib", "ivl"
            )
        os.environ["ICEBOX"] = safe_join(
            base_dir.get("ice40"), "share", "icebox"
        )
        os.environ["TRELLIS"] = safe_join(
            base_dir.get("ecp5"), "share", "trellis"
        )
        os.environ["YOSYS_LIB"] = safe_join(
            base_dir.get("yosys"), "share", "yosys"
        )

        global scons_command
        scons_command = [
            normpath(sys.executable),
            safe_join(bin_dir["scons"], "scons"),
        ]

    return check


def check_package(name, version, spec_version, path):
    """DOC: TODO"""

    # Apio package 'gtkwave' only exists for Windows.
    # Linux and MacOS user must install the native GTKWave.
    if name == "gtkwave" and platform.system() != "Windows":
        return True

    # Check package path
    if not isdir(path):
        show_package_path_error(name)
        show_package_install_instructions(name)
        return False

    # Check package version
    if not check_package_version(version, spec_version):
        show_package_version_warning(name, version, spec_version)
        show_package_install_instructions(name)
        return False

    return True


def check_package_version(version, spec_version):
    """DOC: TODO"""

    spec = semantic_version.SimpleSpec(spec_version)
    try:
        semver = semantic_version.Version(version)
    except ValueError:
        return False

    return semver in spec


def show_package_version_warning(name, version, spec_version):
    """DOC: TODO"""

    message = (
        "Warning: package '{0}' version {1}\n"
        "does not match the semantic version {2}"
    ).format(name, version, spec_version)
    click.secho(message, fg="yellow")


def show_package_path_error(name):
    """DOC: TODO"""

    message = "Error: package '{}' is not installed".format(name)
    click.secho(message, fg="red")


def show_package_install_instructions(name):
    """DOC: TODO"""

    if config_data and _check_apt_get():  # /etc/apio.json file exists
        click.secho(
            "Please run:\n" "   apt-get install apio-{}".format(name),
            fg="yellow",
        )
    else:
        click.secho(
            "Please run:\n" "   apio install {}".format(name), fg="yellow"
        )


def _check_apt_get():
    """Check if apio can be installed through apt-get"""
    check = False
    if "TESTING" not in os.environ:
        result = exec_command(["dpkg", "-l", "apio"])
        if result and result.get("returncode") == 0:
            match = re.findall(r"rc\s+apio", result.get("out")) + re.findall(
                r"ii\s+apio", result.get("out")
            )
            check = len(match) > 0
    return check


def get_package_version(name, profile):
    """DOC: TODO"""

    version = ""
    if name in profile.packages:
        version = profile.packages.get(name).get("version")
    return version


def get_package_spec_version(name, resources):
    """DOC: TODO"""

    spec_version = ""
    if name in resources.distribution.get("packages"):
        spec_version = resources.distribution.get("packages").get(name)
    return spec_version


def change_filemtime(path, time):
    """DOC: TODO"""

    os.utime(path, (time, time))


def exec_command(*args, **kwargs):  # pragma: no cover
    """DOC: TODO"""

    result = {"out": None, "err": None, "returncode": None}

    default = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=platform.system() == "Windows",
    )
    default.update(kwargs)
    kwargs = default

    try:
        proc = subprocess.Popen(*args, **kwargs)
        result["out"], result["err"] = proc.communicate()
        result["returncode"] = proc.returncode
    except KeyboardInterrupt:
        click.secho("Aborted by user", fg="red")
        sys.exit(1)
    except Exception as exc:
        click.secho(str(exc), fg="red")
        sys.exit(1)
    finally:
        for std in ("stdout", "stderr"):
            if isinstance(kwargs[std], AsyncPipe):
                kwargs[std].close()

    _parse_result(kwargs, result)

    return result


def _parse_result(kwargs, result):
    for std in ("stdout", "stderr"):
        if isinstance(kwargs[std], AsyncPipe):
            result[std[3:]] = "\n".join(kwargs[std].get_buffer())

    for k, value in result.items():
        if value and isinstance(value, unicode):
            result[k].strip()


def get_pypi_latest_version():
    """DOC: TODO"""

    req = None
    version = None
    try:
        req = requests.get("https://pypi.python.org/pypi/apio/json")
        version = req.json().get("info").get("version")
        req.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        error_message = str(exc)
        if "NewConnectionError" in error_message:
            click.secho(
                "Error: could not connect to Pypi.\n"
                "Check your internet connection and try again",
                fg="red",
            )
        else:
            click.secho(error_message, fg="red")
    except Exception as exc:
        click.secho("Error: " + str(exc), fg="red")
    finally:
        if req:
            req.close()
    return version


def get_folder(folder):
    """DOC: TODO"""

    return safe_join(dirname(__file__), folder)


def mkdir(path):
    """DOC: TODO"""

    path = dirname(path)
    if not exists(path):
        try:
            os.makedirs(path)
        except OSError:
            pass


def check_dir(_dir):
    """DOC: TODO"""

    if _dir is None:
        _dir = os.getcwd()

    if isfile(_dir):
        click.secho(
            "Error: project directory is already a file: {0}".format(_dir),
            fg="red",
        )
        sys.exit(1)

    if not exists(_dir):
        try:
            os.makedirs(_dir)
        except OSError:
            pass
    return _dir


def command(function):
    """Command decorator"""

    def decorate(*args, **kwargs):
        exit_code = 1
        try:
            exit_code = function(*args, **kwargs)
        except Exception as exc:
            if str(exc):
                click.secho("Error: " + str(exc), fg="red")
        finally:
            return exit_code

    return decorate


def decode(text):
    """DOC: TODO"""

    return jwt.decode(text, "secret", algorithm="HS256")


def get_serial_ports():
    """DOC: TODO"""

    result = []

    for port, description, hwid in comports():
        if not port:
            continue
        if "VID:PID" in hwid:
            result.append(
                {"port": port, "description": description, "hwid": hwid}
            )

    return result


def get_tinyprog_meta():
    """DOC: TODO"""

    _command = join(get_bin_dir(), "tinyprog")
    result = exec_command([_command, "--pyserial", "--meta"])
    try:
        out = unicoder(result.get("out", ""))
        if out:
            return json.loads(out)
    except Exception as exc:
        print(exc)
        return []
    return []


def get_bin_dir():
    """DOC: TODO"""

    candidate = dirname(sys.modules["__main__"].__file__)
    # Windows + virtualenv = 💩
    # In this case the main file is: venv/Scripts/apio.exe/__main__.py!
    # This is not good because venv/Scripts/apio.exe is not a directory
    # So here we go with the workaround:
    if candidate.endswith(".exe"):
        return dirname(candidate)

    return candidate


def get_python_version():
    """DOC: TODO"""

    return "{0}.{1}".format(sys.version_info[0], sys.version_info[1])
