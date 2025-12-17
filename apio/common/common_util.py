# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Utilities that are available for both the apio (parent) process and the
scons (child) process."""

import os
import sys
from pathlib import Path
from glob import glob
from typing import List, Union, Any, Tuple
import debugpy

# -- A list with the file extensions of the source files.
SRC_SUFFIXES = [".v", ".sv"]

# -- The root dir of all the env build directory. Relative to the
# -- project dir. 'ALL' to distinguish from individual env build dirs.
PROJECT_BUILD_PATH = Path("_build")


def env_build_path(env_name: str) -> Path:
    """Given an env name, return a relative path from the project dir to the
    env build dir."""
    return PROJECT_BUILD_PATH / env_name


def maybe_wait_for_remote_debugger(env_var_name: str):
    """A rendezvous point for a remote debugger. If the environment variable
    of given name is set, the function will block until a remote
    debugger (e.g. from Visual Studio Code) is attached.
    """
    if os.getenv(env_var_name) is not None:
        # NOTE: This function may be called before apio_console.py is
        # initialized, so we use print() instead of cout().
        print(f"Env var '{env_var_name}' was detected.")
        print(
            "Setting PYDEVD_DISABLE_FILE_VALIDATION=1 to disable frozen "
            "modules warning."
        )
        os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"
        port = 5678
        print(f"Apio SCons for remote debugger on port localhost:{port}.")
        debugpy.listen(port)
        print(
            "Attach Visual Studio Code python remote python debugger "
            f"to port {port}."
        )
        # -- Make sure the messages to the user are flushed.
        sys.stdout.flush()
        sys.stderr.flush()

        # -- Block until the debugger connects.
        debugpy.wait_for_client()
        # -- Here the remote debugger is attached and the program continues.
        print("Remote debugger is attached, program continues...")


def file_sort_key_func(f: Union[str, Path]) -> Any:
    """Given a file name or path, return a key to sort a file list.
    The order is lexicography and case sensitive."""
    path = Path(f)
    # -- List of directory names in lower case.
    parents: List[str] = [s.lower() for s in path.parent.parts]
    # -- File name in lower case.
    name: str = path.name.lower()
    # -- Sort by directory and then by file name.
    return [parents, name]


def is_source_file(file_name: str) -> bool:
    """Given a file name, determine by its extension if it's a verilog
    source file (testbenches included)."""
    _, ext = os.path.splitext(file_name)
    return ext in SRC_SUFFIXES


def has_testbench_name(file_name: str) -> bool:
    """Given a file name, return true if it's base name indicates a
    testbench. For example abc_tb.v or _build/abc_tb.out. The file extension
    is ignored.
    """
    name, _ = os.path.splitext(file_name)
    return name.lower().endswith("_tb")


def sort_files(files: List[str]) -> List[str]:
    """Sort a list of files by directory and then by file name.
    A new sorted list is returned.
    """
    # -- Sort the files by directory and then by file name.
    return sorted(files, key=file_sort_key_func)


def get_project_source_files() -> Tuple[List[str], List[str]]:
    """Get the list of source files in the directory tree under the current
    directory, splitted into synth and testbench lists.
    If source file has the suffix _tb it's is classified st a testbench,
    otherwise as a synthesis file.
    """
    # -- Get a list of all source files in the project dir.
    # -- Ideally we should use the scons env.Glob() method but it doesn't
    # -- work with the recursive=True option. So we use the glob() function
    # -- instead.
    files: List[str] = []
    for ext in SRC_SUFFIXES:
        files.extend(glob(f"**/*{ext}", recursive=True))

    # -- Sort the files by directory and then by file name.
    files = sort_files(files)

    # -- Split file names to synth files and testbench file lists
    synth_srcs = []
    test_srcs = []
    for file in files:
        if PROJECT_BUILD_PATH in Path(file).parents:
            # -- Ignore source files from the _build directory.
            continue
        if has_testbench_name(file):
            # -- Handle a testbench file.
            test_srcs.append(file)
        else:
            # -- Handle a synthesis file.
            synth_srcs.append(file)

    return (synth_srcs, test_srcs)
