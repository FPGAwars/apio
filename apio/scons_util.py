# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Shared utilities for the various SConstruct.py.  The functions
in this file are intended to be called only from the SConstruct files
and should not be architecture specific.
"""

from typing import Callable, List


def get_constraint_file(
    file_ext: str, glob_func: Callable[[str], List[str]]
) -> str:
    """Returns the name of the constrain file to use.

    file_ext is a string with the constrained file extension. E.g. ".pcf"
    for ice40.

    glob_func is a reference to the scon Glob function.

    Returns the file name or "" if not found.
    """
    # Files in alphabetical order.
    file_names = glob_func(f"*{file_ext}")
    n = len(file_names)
    # Case 1: No matching files.
    if n == 0:
        print(f"Warning: No {file_ext} constraints file.")
        return ""
    # Case 2: Exactly one matching file.
    if n == 1:
        print(f"Info: Found constraint file {file_names[0]}.")
        return file_names[0]
    # Case 3: Multiple matching files.
    print(f"Warning: Found multiple {file_ext} files, using {file_names[0]}.")
    return file_names[0]
