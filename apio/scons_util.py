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

# C0209: Formatting could be an f-string (consider-using-f-string)
# pylint: disable=C0209

# W0613: Unused argument
# pylint: disable=W0613

import os
import re
from platform import system
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
import SCons
from SCons.Script import DefaultEnvironment
from SCons.Script.SConscript import SConsEnvironment
import SCons.Node.FS
import click

# -- Target name
TARGET = "hardware"


def map_params(
    env: SConsEnvironment, params: Optional[List[str]], fmt: str
) -> str:
    """A common function construct a command string snippet from a list
    of arguments. The functon does the following:
     1. If non replace with []
     2. Drops empty items.
     3. Maps the items using the format string which contains exactly one
        placeholder {}.
     4. Joins the items with a white space char.
    """
    # None designates empty list. Avoiding the pylint non safe default warning.
    if params is None:
        params = []

    # Drop empty params and map the rest using the format string.
    mapped_params = [fmt.format(x.strip()) for x in params if x.strip()]

    # Join using a single space.
    return " ".join(mapped_params)


def basename(env: SConsEnvironment, file_name: str) -> str:
    """Given a file name, returns it with the extension removed."""
    result, _ = os.path.splitext(file_name)
    return result


def is_verilog_src(env: SConsEnvironment, file_name: str) -> str:
    """Given a file name, determine by its extension if it's a verilog source
    file (testbenches included)."""
    _, ext = os.path.splitext(file_name)
    return ext == "v"


def is_testbench(env: SConsEnvironment, file_name: str) -> bool:
    """Given a file name, return true if it's a testbench file."""
    name = basename(env, file_name)
    return name.lower().endswith("_tb")


def is_windows(env: SConsEnvironment) -> bool:
    """Returns True if running on Windows."""
    return "Windows" == system()


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


def get_verilator_warning_params(env: SConsEnvironment) -> str:
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


def make_verilog_src_scanner(env: SConsEnvironment) -> SCons.Scanner:
    """Creates and returns a scons Scanner object for scanning verilog
    files for dependencies.
    """
    # A Regex to icestudio propriaetry references for *.list files.
    # Example:
    #   Text:      ' parameter v771499 = "v771499.list"'
    #   Captures:  'v771499.list'
    icestudio_list_re = re.compile(r"[\n|\s][^\/]?\"(.*\.list?)\"", re.M)

    # A regex to match a verilog include.
    # Example
    #   Text:     `include "apio_testing.vh"
    #   Capture:  'apio_testing.vh'
    verilog_include_re = re.compile(
        r'`\s*include\s+["]([a-zA-Z_./]+)["]', re.M
    )

    def verilog_src_scanner_func(
        file_node: SCons.Node.FS.File, env: SConsEnvironment, ignored_path
    ) -> List[str]:
        """Given a Verilog file, scan it and return a list of references
        to other files it depends on. It's not require to report dependency
        on another .v file in the project since scons loads anyway
        all the .v files in the project.

        Returns a list of files.
        """
        # Sanity check. Should be called only to scan verilog files.
        assert file_node.name.lower().endswith(
            ".v"
        ), f"Not a .v file: {file_node.name}"
        includes_set = set()
        file_text = file_node.get_text_contents()
        # Get IceStudio includes.
        includes = icestudio_list_re.findall(file_text)
        includes_set.update(includes)
        # Get Standard verilog includes.
        includes = verilog_include_re.findall(file_text)
        includes_set.update(includes)
        # Get a deterministic list.
        includes_list = sorted(list(includes_set))
        # For debugging
        # info(env, f"*** {file_node.name} includes {includes_list}")
        return env.File(includes_list)

    return env.Scanner(function=verilog_src_scanner_func)


def make_verilator_config_builder(env: SConsEnvironment, config_text: str):
    """Create a scons Builder that writes a verilator config file
    (hardware.vlt) with the given text."""

    def verilator_config_func(target, source, env):
        """Creates a verilator .vlt config files."""
        with open(target[0].get_path(), "w", encoding="utf-8") as target_file:
            target_file.write(config_text)
        return 0

    return env.Builder(
        action=env.Action(
            verilator_config_func, "Creating verilator config file."
        ),
        suffix=".vlt",
    )


def get_source_files(env: SConsEnvironment) -> Tuple[List[str], List[str]]:
    """Get the list of *.v files, splitted into synth and testbench lists.
    If a .v file has the suffix _tb.v it's is classified st a testbench,
    otherwise as a synthesis file.
    """
    # -- Get a list of all *.v files in the project dir.
    files: List[SCons.Node.FS.File] = env.Glob("*.v")

    # Split file names to synth files and testbench file lists
    synth_srcs = []
    test_srcs = []
    for file in files:
        if is_testbench(env, file.name):
            test_srcs.append(file.name)
        else:
            synth_srcs.append(file.name)
    return (synth_srcs, test_srcs)


@dataclass(frozen=True)
class SimulationConfig:
    """Simulation parameters, for sim and test commands."""

    top_module: str  # Top module name of the simulation.
    srcs: List[str]  # List of source files to compile.


def get_sim_config(
    env: SConsEnvironment, testbench: str, synth_srcs: List[str]
) -> SimulationConfig:
    """Returns a SimulationConfig for a sim command. 'testbench' is
    a required testbench file name. 'synth_srcs' is the list of all
    module sources as returned by get_source_files()."""
    # Apio sim requires a testbench arg so ifi this missing here, it's a
    # programming error.
    if not testbench:
        fatal_error(env, "[Internal] Sim testbench name got lost.")

    # Construct a SimulationParams with all the synth files + the
    # testbench file.
    top_module = basename(env, testbench)
    srcs = synth_srcs + [testbench]
    return SimulationConfig(top_module, srcs)


def get_tests_configs(
    env: SConsEnvironment,
    testbench: str,
    synth_srcs: List[str],
    test_srcs: list[str],
) -> List[SimulationConfig]:
    """Return a list of SimulationConfigs for each of the testbenches that
    need to be run for a 'apio test' command. If testbench is empty,
    all the testbenches in test_srcs will be tested. Otherwise, only the
    testbench in testbench will be tested. synth_srcs and test_srcs are
    source and test file lists as returned by get_source_files()."""
    # List of testbenches to be tested.
    if testbench:
        testbenches = testbench
    else:
        testbenches = test_srcs

    # If there are not testbenches, we consider the test as failed.
    if len(testbenches) == 0:
        fatal_error(env, "No testbench files found (*_tb.v).")

    # Construct a config for each testbench.
    configs = []
    for tb in testbenches:
        top_module = basename(env, tb)
        srcs = synth_srcs + [tb]
        configs.append(SimulationConfig(top_module, srcs))

    return configs


def make_waves_target(
    env: SConsEnvironment,
    vcd_file_target: SCons.Node.NodeList,
    top_module: str,
) -> List[SCons.Node.Alias.Alias]:
    """Construct a target to launch the QTWave signal viwer. vcd_file_target is
    the simulator target that generated the vcd file with the signals. Top
    module is to derive the name of the .gtkw which can be used to save the
    viewer configuration for future simulations. Returns the new targets.
    """
    result = env.Alias(
        "sim",
        vcd_file_target,
        "gtkwave {0} {1} {2}.gtkw".format(
            '--rcvar "splash_disable on" --rcvar "do_initial_zoom_fit 1"',
            vcd_file_target[0],
            top_module,
        ),
    )
    return result


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
def make_iverilog_action(
    env: SConsEnvironment,
    *,
    ivl_path: str,
    verbose: bool,
    vcd_output_name: str,
    is_interactive: bool,
    extra_params: List[str] = None,
    lib_dirs: List[str] = None,
    lib_files: List[str] = None,
) -> str:
    """Construct an iverilog scons action string.
    * env: Rhe scons environment.
    * lvl: Optional path to the lvl library.
    * verbose: IVerilog will show extra info.
    * vcd_output_name: Value for the macro VCD_OUTPUT.
    * is_interactive: True for apio sim, False otherwise.
    * extra_params: Optional list of additional IVerilog params.
    * lib_dirs: Optional list of dir pathes to include.
    * lib_files: Optional list of library files to compile.
    *
    * Returns the scons action string for the IVerilog command.
    """
    ivl_path_param = (
        "" if is_windows(env) or not ivl_path else f'-B "{ivl_path}"'
    )

    # Construct the action string.
    action = (
        "iverilog {0} {1} -o $TARGET {2} {3} {4} {5} {6} $SOURCES"
    ).format(
        ivl_path_param,
        "-v" if verbose else "",
        f"-DVCD_OUTPUT={vcd_output_name}",
        "-DINTERACTIVE_SIM" if is_interactive else "",
        map_params(env, extra_params, "{}"),
        map_params(env, lib_dirs, '-I"{}"'),
        map_params(env, lib_files, '"{}"'),
    )

    return action


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
def make_verilator_action(
    env: SConsEnvironment,
    *,
    warnings_all: bool = False,
    warnings_no_style: bool = False,
    no_warns: List[str] = None,
    warns: List[str] = None,
    top_module: str = "",
    extra_params: List[str] = None,
    lib_dirs: List[str] = None,
    lib_files: List[str] = None,
) -> str:
    """Construct an verilator scons action string.
    * env: Rhe scons environment.
    * warnings_all: If True, use -Wall.
    * warnings_no_style: If True, use -Wno-style.
    * no_warns: Optional list with verilator warning codes to disble.
    * warns: Optional list with verilator warning codes to enable.
    * top_module: If not empty, use --top-module <top_module>.
    * extra_params: Optional additional arguments.
    * libs_dirs: Optional directories for include search.
    * lib_files: Optional additional files to include.
    """

    action = (
        "verilator --lint-only --bbox-unsup --timing -Wno-TIMESCALEMOD "
        "-Wno-MULTITOP {0} {1} {2} {3} {4} {5} {6} {7} {8} $SOURCES"
    ).format(
        "-Wall" if warnings_all else "",
        "-Wno-style" if warnings_no_style else "",
        map_params(env, no_warns, "-Wno-{}"),
        map_params(env, warns, "-Wwarn-{}"),
        f"--top-module {top_module}" if top_module else "",
        map_params(env, extra_params, "{}"),
        map_params(env, lib_dirs, '-I"{}"'),
        TARGET + ".vlt",
        map_params(env, lib_files, '"{}"'),
    )

    return action
