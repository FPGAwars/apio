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
from enum import Enum
import json
from typing import Dict, Tuple, List, Optional, NoReturn
from dataclasses import dataclass
import click
from SCons import Scanner
from SCons.Node import NodeList
from SCons.Node.FS import File
from SCons.Node.Alias import Alias
from SCons.Script.SConscript import SConsEnvironment
from SCons.Script import DefaultEnvironment
from SCons.Action import FunctionAction, Action
from SCons.Builder import Builder
import SCons.Defaults


# -- All the build files and other artifcats are created in this this
# -- subdirectory.
BUILD_DIR = "_build"

# -- A shortcut with '/' or '\' appended to the build dir name.
BUILD_DIR_SEP = BUILD_DIR + os.sep

# -- Target name. This is the base file name for various build artifacts.
TARGET = BUILD_DIR_SEP + "hardware"

SUPPORTED_GRAPH_TYPES = ["svg", "pdf", "png"]


class SConstructId(Enum):
    """Identifies the SConstruct script that is running. Used to select
    the desired behavior when it's script dependent."""

    SCONSTRUCT_ICE40 = 1
    SCONSTRUCT_ECP5 = 2
    SCONSTRUCT_GOWIN = 3


def map_params(
    env: SConsEnvironment, params: Optional[List[str]], fmt: str
) -> str:
    """A common function construct a command string snippet from a list
    of arguments. The functon does the following:
     1. If params arg is None replace it with []
     2. Drops empty or white space only items.
     3. Maps the items using the format string which contains exactly one
        placeholder {}.
     4. Joins the items with a white space char.

     For examples, see the unit test at test_scons_util.py.
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
    return ext == ".v"


def has_testbench_name(env: SConsEnvironment, file_name: str) -> bool:
    """Given a file name, return true if it's base name indicates a
    testbench. It can be for example abc_tb.v or _build/abc_tb.out.
    The file extension is ignored.
    """
    name, _ = os.path.splitext(file_name)
    return name.lower().endswith("_tb")


def is_windows(env: SConsEnvironment) -> bool:
    """Returns True if running the platform id represents windows."""
    # -- This bool bar is created when constructing the env.
    val = env["IS_WINDOWS"]
    assert isinstance(val, bool), type(val)
    return val


def create_construction_env(args: Dict[str, str]) -> SConsEnvironment:
    """Creates a scons env. Should be called very early in SConstruct.py"""

    # -- Make sure that the default environment doesn't exist, to make sure
    # -- we create a fresh environment. This is important with pytest which
    # -- can run multiple tests in the same python process.
    # --
    # pylint: disable=protected-access
    assert (
        SCons.Defaults._default_env is None
    ), "DefaultEnvironment already exists"
    # pylint: enable=protected-access

    # Create the env. We don't use the DefaultEnvironment (a singleton) to
    # allow the creation in pytest multiple test environments in the same
    # tesing process.
    env: SConsEnvironment = DefaultEnvironment(ENV=os.environ, tools=[])

    # Add the args dictionary as a new ARGUMENTS var.
    assert env.get("ARGUMENTS") is None
    env.Replace(ARGUMENTS=args)

    # Evaluate the optional force_color arg and set its value
    # an env var on its own.
    assert env.get("FORCE_COLORS") is None
    env.Replace(FORCE_COLORS=False)  # Tentative, so we can call arg_bool.
    flag = arg_bool(env, "force_colors", False)
    env.Replace(FORCE_COLORS=flag)
    # Set the IS_WINDOWS flag based on the required "platform_id" arg.
    platform_id = arg_str(env, "platform_id", "")
    # Note: this is a programming error, not a user error.
    assert platform_id, "Missing required scons arg 'platform_id'."
    flag = "windows" in platform_id.lower()
    assert env.get("IS_WINDOWS") is None
    env.Replace(IS_WINDOWS=flag)  # Tentative.

    # For debugging.
    # dump_env_vars(env)

    return env


def __dump_parsed_arg(env, name, value, from_default: bool) -> None:
    """Used to dump parsed scons arg. For debugging only."""
    # Uncomment below for debugging.
    # type_name = type(value).__name__
    # default = "(default)" if from_default else ""
    # click.secho(
    #     f"Arg  {name:15} ->  {str(value):15} " f"{type_name:6} {default}"
    # )


def get_args(env: SConsEnvironment) -> Dict[str, str]:
    """Returns the SConstrcuct invocation args."""
    return env["ARGUMENTS"]


def arg_bool(env: SConsEnvironment, name: str, default: bool) -> bool:
    """Parse and return a boolean arg."""
    assert isinstance(default, bool) or default is None, f"{name}: {default}"
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
    assert isinstance(default, str) or default is None, f"{name}: {default}"
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

    NOTE: As of Oct 2024, forcing colors from the scons subprocess does not
    work on Windows and as result, scons output is colorless.
    For more details see the click issue at
    https://github.com/pallets/click/issues/2791.
    """
    flag = env["FORCE_COLORS"]
    assert isinstance(flag, bool)
    return flag


def msg(env: SConsEnvironment, text: str, fg: str = None) -> None:
    """Print a message to the user. Similar to click.secho but with
    proper color enforcement.
    """
    click.secho(text, fg=fg, color=force_colors(env))


def info(env: SConsEnvironment, text: str) -> None:
    """Prints a short info message and continue."""
    msg(env, f"Info: {text}")


def warning(env: SConsEnvironment, text: str) -> None:
    """Prints a short warning message and continue."""
    msg(env, f"Warning: {text}", fg="yellow")


def error(env: SConsEnvironment, text: str) -> None:
    """Prints a short error message and continue."""
    msg(env, f"Error: {text}", fg="red")


def fatal_error(env: SConsEnvironment, text: str) -> NoReturn:
    """Prints a short error message and exit with an error code."""
    error(env, text)
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
        return result
    # Case 3: Multiple matching files.
    fatal_error(
        env, f"Found multiple '*{file_ext}' constrain files, expecting one."
    )


def dump_env_vars(env: SConsEnvironment) -> None:
    """Prints a list of the environment variables. For debugging."""
    dictionary = env.Dictionary()
    keys = list(dictionary.keys())
    keys.sort()
    print("----- Env vars begin -----")
    for key in keys:
        print(f"{key} = {env[key]}")
    print("----- Env vars end -------")


def get_programmer_cmd(env: SConsEnvironment) -> str:
    """Return the programmer command as derived from the scons "prog" arg."""

    # Get the programer command template arg.
    prog_arg = arg_str(env, "prog", "")

    # If empty then return as is. This must be an apio command that doesn't use
    # the programmer.
    if not prog_arg:
        return prog_arg

    # It's an error if the programmer command doesn't have the $SOURCE
    # placeholder when scons inserts the binary file name.
    if "$SOURCE" not in prog_arg:
        fatal_error(
            env,
            "[Internal] 'prog' argument does not contain "
            f"the '$SOURCE' marker. [{prog_arg}]",
        )

    return prog_arg


# A regex to identify "$dumpfile(" in testbenches.
testbench_dumpfile_re = re.compile(r"[$]dumpfile\s*[(]")


def get_source_file_issue_action(env: SConsEnvironment) -> FunctionAction:
    """Returns a SCons action that scans the source files and print
    error or warning messages about issues it finds."""

    def report_source_files_issues(
        source: List[File],
        target: List[Alias],
        env: SConsEnvironment,
    ):
        """The scanner function.."""

        for file in source:

            # --For now we report issues only in testbenches so skip otherwise.
            if not is_verilog_src(env, file.name) or not has_testbench_name(
                env, file.name
            ):
                continue

            # -- Read the testbench file text.
            file_text = file.get_text_contents()

            # -- if contains $dumpfile, print a warning.
            if testbench_dumpfile_re.findall(file_text):
                msg(
                    env,
                    f"Warning: [{file.name}] Using $dumpfile() in apio "
                    "testbenches is not recomanded.",
                    fg="magenta",
                )

    return Action(report_source_files_issues, "Scanning for issues.")


def make_verilog_src_scanner(env: SConsEnvironment) -> Scanner.Base:
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
        file_node: File, env: SConsEnvironment, ignored_path
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
        # If the file doesn't exist, this returns an empty string.
        file_text = file_node.get_text_contents()
        # Get IceStudio includes.
        includes = icestudio_list_re.findall(file_text)
        includes_set.update(includes)
        # Get Standard verilog includes.
        includes = verilog_include_re.findall(file_text)
        includes_set.update(includes)
        # Get a deterministic list. (Does it sort by file.name?)
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

    return Builder(
        action=Action(
            verilator_config_func, "Creating verilator config file."
        ),
        suffix=".vlt",
    )


def make_dot_builder(
    env: SConsEnvironment,
    top_module: str,
    verilog_src_scanner,
    verbose: bool,
):
    """Creates and returns an SCons dot builder that generates the graph
    in .dot format.

    'verilog_src_scanner' is a verilog file scanner that identify additional
    dependencies for the build, for example, icestudio propriety includes.
    """

    # -- The builder.
    dot_builder = Builder(
        action=(
            'yosys -f verilog -p "show -format dot -colors 1 '
            '-prefix {0}hardware {1}" {2} $SOURCES'
        ).format(
            BUILD_DIR_SEP,
            top_module if top_module else "unknown_top",
            "" if verbose else "-q",
        ),
        suffix=".dot",
        src_suffix=".v",
        source_scanner=verilog_src_scanner,
    )

    return dot_builder


def make_graphviz_builder(
    env: SConsEnvironment,
    graph_spec: str,
):
    """Creates and returns an SCons graphviz builder that renders
    a .dot file to one of the supported formats.

    'graph_spec' contains the rendering specification and currently
    it includes a single value which is the target file format".
    """

    # --Decode the graphic spec. Currently it's trivial since it
    # -- contains a single value.
    if graph_spec:
        # -- This is the case when scons target is 'graph'.
        graph_type = graph_spec
        assert graph_type in SUPPORTED_GRAPH_TYPES, graph_type
    else:
        # -- This is the case when scons target is not 'graph'.
        graph_type = "svg"

    def completion_action(source, target, env):
        """Action function that prints a completion message."""
        msg(env, f"Generated {TARGET}.{graph_type}", fg="green")

    actions = [
        f"dot -T{graph_type} $SOURCES -o $TARGET",
        Action(completion_action, "completion_action"),
    ]

    graphviz_builder = Builder(
        # Expecting graphviz dot to be installed and in the path.
        action=actions,
        suffix=f".{graph_type}",
        src_suffix=".dot",
    )

    return graphviz_builder


def get_source_files(env: SConsEnvironment) -> Tuple[List[str], List[str]]:
    """Get the list of *.v files, splitted into synth and testbench lists.
    If a .v file has the suffix _tb.v it's is classified st a testbench,
    otherwise as a synthesis file.
    """
    # -- Get a list of all *.v files in the project dir.
    files: List[File] = env.Glob("*.v")

    # Split file names to synth files and testbench file lists
    synth_srcs = []
    test_srcs = []
    for file in files:
        if has_testbench_name(env, file.name):
            test_srcs.append(file.name)
        else:
            synth_srcs.append(file.name)
    return (synth_srcs, test_srcs)


@dataclass(frozen=True)
class SimulationConfig:
    """Simulation parameters, for sim and test commands."""

    testbench_name: str  # The testbench name, without the 'v' suffix.
    build_testbench_name: str  # testbench_name prefixed by build dir.
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
    testbench_name = basename(env, testbench)
    build_testbench_name = BUILD_DIR_SEP + testbench_name
    srcs = synth_srcs + [testbench]
    return SimulationConfig(testbench_name, build_testbench_name, srcs)


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
        testbench_name = basename(env, tb)
        build_testbench_name = BUILD_DIR_SEP + testbench_name
        srcs = synth_srcs + [tb]
        configs.append(
            SimulationConfig(testbench_name, build_testbench_name, srcs)
        )

    return configs


def make_waves_target(
    env: SConsEnvironment,
    vcd_file_target: NodeList,
    sim_config: SimulationConfig,
) -> List[Alias]:
    """Construct a target to launch the QTWave signal viwer. vcd_file_target is
    the simulator target that generated the vcd file with the signals.
    Returns the new targets.
    """

    # -- Construct the commands list.
    commands = []

    # -- On windows we need to setup the cache. This could be done once
    # -- when the oss-cad-suite is installed but since we currently don't
    # -- have a package setup mechanism, we do it here on each invocation.
    # -- The time penalty is negligible.
    # -- With the stock oss-cad-suite windows package, this is done in the
    # -- environment.bat script.
    if is_windows(env):
        commands.append("gdk-pixbuf-query-loaders --update-cache")

    # -- The actual wave viewer command.
    commands.append(
        "gtkwave {0} {1} {2}.gtkw".format(
            '--rcvar "splash_disable on" --rcvar "do_initial_zoom_fit 1"',
            vcd_file_target[0],
            sim_config.testbench_name,
        )
    )

    result = env.Alias(
        "sim",
        vcd_file_target,
        commands,
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

    # Escaping for windows. '\' -> '\\'
    escaped_vcd_output_name = vcd_output_name.replace("\\", "\\\\")

    # -- Construct the action string.
    action = (
        "iverilog {0} {1} -o $TARGET {2} {3} {4} {5} {6} $SOURCES"
    ).format(
        ivl_path_param,
        "-v" if verbose else "",
        f"-DVCD_OUTPUT={escaped_vcd_output_name}",
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
        "verilator_bin --lint-only --quiet --bbox-unsup --timing "
        "-Wno-TIMESCALEMOD -Wno-MULTITOP "
        "{0} {1} {2} {3} {4} {5} {6} {7} {8} $SOURCES"
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


# pylint: disable=too-many-locals
def _print_pnr_report(
    env: SConsEnvironment,
    json_txt: str,
    script_id: SConstructId,
    verbose: bool,
) -> None:
    """Accepts the text of the pnr json report and prints it in
    a user friendly way. Used by the 'apio report' command."""
    # -- Json text to tree of Dicts.
    report: Dict[str, any] = json.loads(json_txt)

    # --- Report utilization
    msg(env, "")
    msg(env, "UTILIZATION:", fg="cyan")
    utilization = report["utilization"]
    for resource, vals in utilization.items():
        available = vals["available"]
        used = vals["used"]
        percents = int(100 * used / available)
        fg = "magenta" if used > 0 else None
        msg(
            env, f"{resource:>20}: {used:5} {available:5} {percents:5}%", fg=fg
        )

    # -- Report max clock speeds.
    # --
    # -- NOTE: As of Oct 2024, some projects do not generate timing
    # -- information and this is being investigated.
    # -- See https://github.com/FPGAwars/icestudio/issues/774 for details.
    msg(env, "")
    msg(env, "CLOCKS:", fg="cyan")
    clocks = report["fmax"]
    if len(clocks) > 0:
        for clk_net, vals in clocks.items():
            # pylint: disable=fixme
            # TODO: Confirm clk name extraction for Gowin.
            # Extract clock name from the net name.
            if script_id == SConstructId.SCONSTRUCT_ECP5:
                # E.g. '$glbnet$CLK$TRELLIS_IO_IN' -> 'CLK'
                clk_signal = clk_net.split("$")[2]
            else:
                # E.g. 'vclk$SB_IO_IN_$glb_clk' -> 'vclk'
                clk_signal = clk_net.split("$")[0]
            # Report speed.
            max_mhz = vals["achieved"]
            styled_max_mhz = click.style(f"{max_mhz:7.2f}", fg="magenta")
            msg(env, f"{clk_signal:>20}: {styled_max_mhz} Mhz max")

    # -- For now we ignore the critical path report in the pnr report and
    # -- refer the user to the pnr verbose output.
    msg(env, "")
    if not verbose:
        msg(env, "Use 'apio report --verbose' for more details.", fg="yellow")


def get_report_action(
    env: SConsEnvironment, script_id: SConstructId, verbose: bool
) -> FunctionAction:
    """Returns a SCons action to format and print the PNR reort from the
    PNR json report file. Used by the 'apio report' command.
    'script_id' identifies the calling SConstruct script and 'verbose'
    indicates if the --verbose flag was invoked."""

    def print_pnr_report(
        source: List[File],
        target: List[Alias],
        env: SConsEnvironment,
    ):
        """Action function. Loads the pnr json report and print in a user
        friendly way."""
        json_file: File = source[0]
        json_txt: str = json_file.get_text_contents()
        _print_pnr_report(env, json_txt, script_id, verbose)

    return Action(print_pnr_report, "Formatting pnr report.")


# Enable for debugging a scons process and call from SConstruct.
#
# def wait_for_remote_debugger():
#     """For developement only. Useful for debugging SConstruct scripts that
#     apio runs as a subprocesses. Call this from the SCconstruct script, run
#     apio from a command line, and then connect with the Visual Studio Code
#     debugger using the launch.json debug target. Can also be used to debug
#     apio itself, without having to create or modify the Visual Studio Code
#     debug targets in launch.json"""

#     # -- We require this import only when using the debugger.
#     import debugpy

#     # -- 5678 is the default debugger port.
#     port = 5678
#     print(f"Waiting for remote debugger on port localhost:{port}.")
#     debugpy.listen(port)
#     print("Attach with the Visual Studio Code debugger.")
#     debugpy.wait_for_client()
#     print("Remote debugger is attached.")


def set_up_cleanup(env: SConsEnvironment) -> None:
    """Should be called only when the "clean" target is specified. Configures
    in scons env do delete all the files in the build directory.
    """

    # -- Should be called only when the 'clean' target is specified.
    # -- If this fails, this is a programming error and not a user error.
    assert env.GetOption("clean"), "Option 'clean' is missing."

    # -- Get the list of all files to clean. Scons adds to the list non
    # -- existing files from other targets it encountered.
    files_to_clean = (
        env.Glob(f"{BUILD_DIR_SEP}*")
        + env.Glob("zadig.ini")
        + env.Glob(".sconsign.dblite")
        + env.Glob("_build")
    )

    # pylint: disable=fixme
    # -- TODO: Remove the cleanup of legacy files after releasing the first
    # -- release with the _build directory.
    # --
    # --
    # -- Until apio 0.9.6, the build artifacts were created in the project
    # -- directory rather than the _build directory. To simplify the transition
    # -- we clean here also left over files from 0.9.5.
    legacy_files_to_clean = (
        env.Glob("hardware.*") + env.Glob("*_tb.vcd") + env.Glob("*_tb.out")
    )

    if legacy_files_to_clean:
        msg(
            env,
            "Deleting also left-over files from previous release.",
            fg="yellow",
        )

        files_to_clean.extend(legacy_files_to_clean)

    # -- Create a dummy target.  I
    dummy_target = env.Command("cleanup-target", "", "")

    # -- Associate all the files with the dummy target.
    env.Clean(dummy_target, files_to_clean)
