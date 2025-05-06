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
import functools
from pathlib import Path
from typing import List, Union
import debugpy
from apio.common.apio_styles import EMPH3, SUCCESS


def maybe_wait_for_remote_debugger(env_var_name: str):
    """A rendezvous point for a remote debugger. If the environment variable
    of given name is set, the function will block until a remote
    debugger (e.g. from Visual Studio Code) is attached.
    """
    if os.getenv(env_var_name) is not None:
        # NOTE: This function may be called before apio_console.py is
        # initialized, so we use print() instead of cout().
        print(f"Env var '{env_var_name}' was detected.")
        port = 5678
        print(f"Apio SCons for remote debugger on port localhost:{port}.")
        debugpy.listen(port)
        print(
            "Attach Visual Studio Code python remote python debugger "
            f"to port {port}.",
            style=EMPH3,
        )
        # -- Block until the debugger connects.
        debugpy.wait_for_client()
        # -- Here the remote debugger is attached and the program continues.
        print(
            "Remote debugger is attached, program continues...",
            style=SUCCESS,
        )


def file_sort_compare_func(a: Union[str, Path], b: Union[str, Path]) -> int:
    """Compare functions for sorting files. It sorts first by directory
    and then by file name. Returns -1 if a < b, 0 if a == b and 1 if a > b."""
    # -- files as Path objects.
    path1 = Path(a)
    path2 = Path(b)

    # -- List of parents.
    parents1: List[str] = [s.lower() for s in path1.parent.parts]
    parents2: List[str] = [s.lower() for s in path2.parent.parts]

    # -- Key to sort by parents and then by name.
    key1 = [parents1, path1.name.lower()]
    key2 = [parents2, path2.name.lower()]

    # -- Resolve as -1, 0 or 1.
    return (key1 > key2) - (key1 < key2)


def sort_files(files: List[str]) -> List[str]:
    """Sort a list of files by directory and then by file name.
    A new sorted list is returned.
    """
    # -- Sort the files by directory and then by file name.
    return sorted(files, key=functools.cmp_to_key(file_sort_compare_func))
