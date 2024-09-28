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

import os
from typing import Dict
from SCons.Script import DefaultEnvironment
from SCons.Script.SConscript import SConsEnvironment
import click


def create_construction_env(args: Dict[str, str]) -> SConsEnvironment:
    """Creates a scons env. Should be called very early in SConstruct.py"""
    # Create the default env.
    env: SConsEnvironment = DefaultEnvironment(ENV=os.environ, tools=[])

    # Add the args dictionary as a new ARGUMENTS var.
    assert env.get("ARGUMENTS") is None
    env.Replace(ARGUMENTS=args)

    # Evaluate the optional force_color arg and set its value
    # an env var on its own.
    assert env.get("FORCE_COLORS") is None
    env.Replace(FORCE_COLORS=False)  # Tentative.
    flag = arg_bool(env, "force_colors", False)
    env.Replace(FORCE_COLORS=flag)  # Tentative.
    if not flag:
        warning(env, "Not forcing scons text colors.")

    # For debugging.
    # dump_env_vars(env)

    return env


def __dump_parsed_arg(env, name, value, from_default: bool) -> None:
    """Used to dump parsed scons arg. For debugging only."""
    # Uncomment below for debugging.
    # type_name = type(value).__name__
    # default = "(default)" if from_default else ""
    # click.echo(f"Arg  {name:15} ->  {str(value):15} {type_name:6} {default}")


def get_args(env: SConsEnvironment) -> Dict[str, str]:
    """Returns the SConstrcuct invocation args."""
    return env["ARGUMENTS"]


def arg_bool(env: SConsEnvironment, name: str, default: bool) -> bool:
    """Parse and return a boolean arg."""
    args = get_args(env)
    raw_value = args.get(name, None)
    if raw_value is None:
        value = default
    else:
        value = {"True": True, "False": False, True: True, False: False}[
            raw_value
        ]
        if value is None:
            fatal_error(
                env, f"Invalid boolean argument '{name} = '{raw_value}'."
            )
    __dump_parsed_arg(env, name, value, from_default=raw_value is None)
    return value


def arg_str(env: SConsEnvironment, name: str, default: str) -> str:
    """Parse and return a string arg."""
    args = get_args(env)
    raw_value = args.get(name, None)
    value = default if raw_value is None else raw_value
    __dump_parsed_arg(env, name, value, from_default=raw_value is None)
    return value


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
    print("----- Env vars begin -----")
    for key in keys:
        print(f"{key} = {env[key]}")
    print("----- Env vars end -------")


def get_verilator_param_str(env: SConsEnvironment) -> str:
    """Construct from the nowwarn and warn arguments an option list
    for verilator. These values are specified by the user to the
    apio lint param.

    To test:  apio lint --warn aaa,bbb  --nowarn ccc,ddd
    """

    no_warn_list = arg_str(env, "nowarn", "").split(",")
    warn_list = arg_str(env, "warn", "").split(",")
    # No warn.
    result = ""
    for warn in no_warn_list:
        if warn != "":
            result += " -Wno-" + warn
    # Warn.
    for warn in warn_list:
        if warn != "":
            result += " -Wwarn-" + warn

    return result


def get_programmer_cmd(env: SConsEnvironment) -> str:
    """Return the programmer command as derived from the scons "prog" arg."""

    # Get the programer command template arg.
    prog_arg = arg_str(env, "prog", "")

    # If empty then return as is.
    if not prog_arg:
        return prog_arg

    # The programmer template is expected to contain the placeholder
    # "${SOURCE}" that we need to convert to "$SOURCE" as expected by scons.
    if "${SOURCE}" not in prog_arg:
        fatal_error(
            env,
            "[Internal] 'prog' argument does not contain "
            f"the '${{SOURCE}}' marker. [{prog_arg}]",
        )

    prog_cmd = prog_arg.replace("${SOURCE}", "$SOURCE")
    return prog_cmd
