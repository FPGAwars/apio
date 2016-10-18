# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2

import os
import click
import subprocess
import json
import re
from os.path import expanduser, isdir, join, isfile
from os import pathsep
from platform import system, uname
from threading import Thread
from string import split

import requests
requests.packages.urllib3.disable_warnings()

__version__ = None

# Python3 compat
try:
    unicode = str
except NameError:  # pragma: no cover
    pass


class ApioException(Exception):

    MESSAGE = None

    def __str__(self):  # pragma: no cover
        if self.MESSAGE:
            return self.MESSAGE.format(*self.args)
        else:
            return Exception.__str__(self)


class AbortedByUser(ApioException):

    MESSAGE = "Aborted by user"


class AsyncPipe(Thread):  # pragma: no cover

    def __init__(self, outcallback=None):
        Thread.__init__(self)
        self.outcallback = outcallback

        self._fd_read, self._fd_write = os.pipe()
        self._pipe_reader = os.fdopen(self._fd_read)
        self._buffer = []

        self.start()

    def get_buffer(self):
        return self._buffer

    def fileno(self):
        return self._fd_write

    def run(self):
        for line in iter(self._pipe_reader.readline, ""):
            line = line.strip()
            self._buffer.append(line)
            if self.outcallback:
                self.outcallback(line)
            else:
                print(line)
        self._pipe_reader.close()

    def close(self):
        os.close(self._fd_write)
        self.join()


def get_systype():
    data = uname()
    arch = ''
    type_ = data[0].lower()
    if type_ == 'linux':
        arch = data[4].lower() if data[4] else ""
    return "%s_%s" % (type_, arch) if arch else type_


class ConfigLoader:
    __shared_state = {}
    loaded = 0
    def __init__(self):
        self.__dict__ = self.__shared_state
        if not self.loaded:
           self.config_data = None
           filepath = os.path.join(os.sep, 'etc', 'apio.json')
           if isfile(filepath):
               with open(filepath, 'r') as f:
                   # Load the JSON file
                   #click.echo('Loading json config\n')
                   self.loaded = 1
                   self.config_data = json.loads(f.read())


def _get_projconf_option_dir(name, default=None):
    _env_name = "APIO_%s" % name.upper()
    from_config = ConfigLoader().config_data[_env_name];
    if from_config:
        return from_config
    if _env_name in os.environ:
        return os.getenv(_env_name)
    return default


def _is_writable(directory):
    try:
        filename = os.path.join(directory, '__test__')
        f = open(filename, "w")
        f.close()
        os.remove(filename)
        return True
    except Exception as e:
        return False

def get_home_dir():
    home_dir = _get_projconf_option_dir("home_dir", "~/.apio")
    home_dir = re.sub(r'\~', expanduser("~"), home_dir)

    paths = split(home_dir, pathsep)
    for path in paths:
        if isdir(path):
           if _is_writable(path):
              return path

    for path in paths:
        if not isdir(path):
           try:
               os.makedirs(path)
               return path
           except OSError as ioex:
               if ioex.errno == 13:
                    click.secho('Warning: can\'t create '+home_dir,
                         fg='yellow')
                    pass

    click.secho('Error: no usable home directory', fg='red')
    return path


def get_package_dir(pkg_name):
    home_dir = _get_projconf_option_dir("home_dir", "~/.apio")
    home_dir = re.sub(r'\~', expanduser("~"), home_dir)

    file_found = 0
    paths = split(home_dir, pathsep)
    for path in paths:
        try_name = join(path, 'packages', pkg_name)
        #click.echo('Trying '+try_name)
        if isdir(try_name):
           file_found = 1
           break

    if file_found:
       return try_name
    else:
       return join(paths[0], 'packages', pkg_name)


def get_project_dir():
    return os.getcwd()


def change_filemtime(path, time):
    os.utime(path, (time, time))


def exec_command(*args, **kwargs):  # pragma: no cover
    result = {
        "out": None,
        "err": None,
        "returncode": None
    }

    default = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=system() == "Windows"
    )
    default.update(kwargs)
    kwargs = default

    p = subprocess.Popen(*args, **kwargs)
    try:
        result['out'], result['err'] = p.communicate()
        result['returncode'] = p.returncode
    except KeyboardInterrupt:
        raise AbortedByUser()
    finally:
        for s in ("stdout", "stderr"):
            if isinstance(kwargs[s], AsyncPipe):
                kwargs[s].close()

    for s in ("stdout", "stderr"):
        if isinstance(kwargs[s], AsyncPipe):
            result[s[3:]] = "\n".join(kwargs[s].get_buffer())

    for k, v in result.items():
        if v and isinstance(v, unicode):
            result[k].strip()

    return result


def get_pypi_latest_version():
    r = None
    version = None
    try:
        r = requests.get("https://pypi.python.org/pypi/apio/json")
        version = r.json()['info']['version']
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        click.secho('Error: Could not connect to Pypi.\n'
                    'Check your internet connection and try again', fg='red')
    except Exception as e:
        click.secho('Error: ' + str(e), fg='red')
    finally:
        if r:
            r.close()
    return version
