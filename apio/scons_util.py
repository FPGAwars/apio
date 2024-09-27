# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Shared utilities for the various SConstruct.py.  Functions here should
be called only from the SConstruct.py files.
"""

# NOTE: We pass the scons construction environment 'env' to the functions
# below, even when not used, to discourage calling these from outside of a
# SConstruct script.
# pylint: disable=unused-argument

from typing import Dict
from SCons.Script.SConscript import SConsEnvironment
import click


def update_env_force_colors(
    env: SConsEnvironment, args: Dict[str, str]
) -> None:
    """Sets the env FORCE_COLORS variable from the SConstruct arguments.
    The apio app passes to the scons subprocess the variable force_colors=True
    to preserved the text colors in the piped stdout.
    """
    raw_flag = args.get("force_colors", False)
    flag = {"True": True, "False": False, False: False}[raw_flag]
    assert isinstance(flag, bool)
    env.Replace(FORCE_COLORS=flag)
    if not flag:
        warning(env, "Not forcing scons text colors.")


def force_colors(env: SConsEnvironment) -> bool:
    """Test if click.secho should be forced, even if piped.

    By default click stips text colors when the stdout is piped,
    for example from the scons subprocess to the apio app. To preserve
    the sconstruct text colors, the apio app passes to the sconstract
    scripts a flag to force the preservation of colors.
    """
    flag = env["FORCE_COLORS"]
    assert isinstance(flag, bool)
    return flag


def info(env: SConsEnvironment, msg: str) -> None:
    """Prints a short info message and continue."""
    click.secho(f"Info: {msg}")


def warning(env: SConsEnvironment, msg: str) -> None:
    """Prints a short warning message and continue."""
    click.secho(f"Warning: {msg}", fg="yellow", color=force_colors(env))


def error(env: SConsEnvironment, msg: str) -> None:
    """Prints a short error message and continue."""
    click.secho(f"Error: {msg}", fg="red", color=force_colors(env))


def fatal_error(env: SConsEnvironment, msg: str) -> None:
    """Prints a short error message and exit with an error code."""
    error(env, msg)
    env.Exit(1)


def get_constraint_file(
    env: SConsEnvironment, file_ext: str, top_module: str
) -> str:
    """Returns the name of the constrain file to use.

    env is the sconstrution environment.

    file_ext is a string with the constrained file extension.
    E.g. ".pcf" for ice40.

    top_module is the top module name. It's is used to construct the
    default file name.

    Returns the file name if found or a default name otherwise otherwise.
    """
    # Files in alphabetical order.
    files = env.Glob(f"*{file_ext}")
    n = len(files)
    # Case 1: No matching files.
    if n == 0:
        result = f"{top_module.lower()}{file_ext}"
        warning(env, f"No {file_ext} constraints file, assuming '{result}'.")
        return result
    # Case 2: Exactly one file found.
    if n == 1:
        result = str(files[0])
        info(env, f"Found constraint file '{result}'.")
        return result
    # Case 3: Multiple matching files. Pick the first file (alphabetically).
    # We could improve the heuristic here, e.g. to prefer a file with
    # the top_module name, if exists.
    result = str(files[0])
    warning(env, f"Found multiple {file_ext} files, using '{result}'.")
    return result


def dump_env_vars(env: SConsEnvironment) -> None:
    """Prints a list of the environment variables. For debugging."""
    dictionary = env.Dictionary()
    keys = list(dictionary.keys())
    keys.sort()
    for key in keys:
        print(f"{key} = {env[key]}")
