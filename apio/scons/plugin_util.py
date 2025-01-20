# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Helper functions for apio scons plugins.
"""

# pylint: disable=consider-using-f-string

import sys
import os
import re
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from click import secho, style
from SCons import Scanner
from SCons.Builder import Builder
from SCons.Action import FunctionAction, Action
from SCons.Node.FS import File
from SCons.Script.SConscript import SConsEnvironment
from SCons.Node import NodeList
from SCons.Node.Alias import Alias
import debugpy
from apio.scons.apio_env import ApioEnv, TARGET, BUILD_DIR_SEP

# -- A list with the file extensions of the verilog source files.
SRC_SUFFIXES = [".v", ".sv"]

TESTBENCH_HINT = "Testbench file names must end with '_tb.v' or '_tb.sv."


def secho_lines(colors: List[str], lines: List[str]) -> None:
    """Secho list of lines with matching colors. If running out of colors,
    repeat the last one.."""
    for i, line in enumerate(lines):
        fg = colors[i] if i < len(colors) else colors[-1]
        secho(line, fg=fg, bold=True, color=True)


def maybe_wait_for_remote_debugger(env_var_name: str):
    """A rendezvous point for a remote debger. If the environment variable
    of given name is set, the function will block until a remote
    debugger (e.g. from Visual Studio Code) is attached.
    """
    if os.getenv(env_var_name) is not None:
        secho(f"Env var '{env_var_name}' was detected.")
        port = 5678
        secho(f"Apio SCons for remote debugger on port localhost:{port}.")
        debugpy.listen(port)
        secho(
            "Attach Visual Studio Code python remote python debugger "
            f"to port {port}.",
            fg="magenta",
            color=True,
        )
        # -- Block until the debugger connetcs.
        debugpy.wait_for_client()
        # -- Here the remote debugger is attached and the program continues.
        secho(
            "Remote debugger is attached, program continues...",
            fg="green",
            color=True,
        )


def map_params(params: Optional[List[str]], fmt: str) -> str:
    """A common function construct a command string snippet from a list
    of arguments. The functon does the following:
    1. If params arg is None replace it with []
    2. Drops empty or white space only items.
    3. Maps the items using the format string which contains exactly one
        placeholder {}.
    4. Joins the items with a white space char.

    For examples, see the unit test at test_scons_util.py.
    """
    # None designates empty list. Avoiding the pylint non safe default
    # warning.
    if params is None:
        params = []

    # Drop empty params and map the rest using the format string.
    mapped_params = [fmt.format(x.strip()) for x in params if x.strip()]

    # Join using a single space.
    return " ".join(mapped_params)


def get_constraint_file(
    apio_env: ApioEnv, file_ext: str, top_module: str
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
    files = apio_env.scons_env.Glob(f"*{file_ext}")
    n = len(files)
    # Case 1: No matching files.
    if n == 0:
        result = f"{top_module.lower()}{file_ext}"
        secho(
            f"Warning: No {file_ext} constraints file, assuming '{result}'.",
            fg="yellow",
            color=True,
        )
        return result
    # Case 2: Exactly one file found.
    if n == 1:
        result = str(files[0])
        return result
    # Case 3: Multiple matching files.
    secho(
        f"Error: Found multiple '*{file_ext}' "
        "constrain files, expecting exactly one.",
        fg="red",
        color=True,
    )
    sys.exit(1)


def verilog_src_scanner(apio_env: ApioEnv) -> Scanner.Base:
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

    # A regex for inclusion via $readmemh()
    # Example
    #   Test:      '$readmemh("my_data.hex", State_buff);'
    #   Capture:   'my_data.hex'
    readmemh_reference_re = re.compile(
        r"\$readmemh\([\'\"]([^\'\"]+)[\'\"]", re.M
    )

    # -- List of required and optional files that may require a rebuild if
    # -- changed.
    core_dependencies = [
        "apio.ini",
        "boards.jsonc",
        "fpgas.jsonc",
        "programmers.jsonc",
    ]

    def verilog_src_scanner_func(
        file_node: File, env: SConsEnvironment, ignored_path
    ) -> List[str]:
        """Given a Verilog file, scan it and return a list of references
        to other files it depends on. It's not require to report dependency
        on another .v file in the project since scons loads anyway
        all the .v files in the project.

        Returns a list of files. Dependencies that don't have an existing
        file are ignored and not returned. This is to avoid references in
        commented out code to break scons dependencies.
        """
        _ = env  # Unused

        # Sanity check. Should be called only to scan verilog files. If
        # this fails, this is a programming error rather than a user error.
        assert is_verilog_src(
            file_node.name
        ), f"Not a src file: {file_node.name}"

        # Create the initial set with the core dependencies.
        candidates_set = set()
        candidates_set.update(core_dependencies)

        # Read the file. This returns [] if the file doesn't exist.
        file_content = file_node.get_text_contents()

        # Get verilog includes references.
        candidates_set.update(verilog_include_re.findall(file_content))

        # Get $readmemh() function references.
        candidates_set.update(readmemh_reference_re.findall(file_content))

        # Get IceStudio references.
        candidates_set.update(icestudio_list_re.findall(file_content))

        # Filter out candidates that don't have a matching files to prevert
        # breakign the build. This handle for example the case where the
        # file references is in a comment or non reachable code.
        # See also https://stackoverflow.com/q/79302552/15038713
        dependencies = []
        for dependency in candidates_set:
            if Path(dependency).exists():
                dependencies.append(dependency)
            elif apio_env.is_debug:
                secho(
                    f"Dependency candidate {dependency} does not exist, "
                    "droping."
                )

        # Sort the strings for determinism.
        dependencies = sorted(list(dependencies))

        # Debug info.
        if apio_env.is_debug:
            secho(f"Dependencies of {file_node.name}:", fg="blue", color=True)
            for dependency in dependencies:
                secho(f"  {dependency}", fg="blue", color=True)

        # All done
        return apio_env.scons_env.File(dependencies)

    return apio_env.scons_env.Scanner(function=verilog_src_scanner_func)


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
def verilator_lint_action(
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
        map_params(no_warns, "-Wno-{}"),
        map_params(warns, "-Wwarn-{}"),
        f"--top-module {top_module}" if top_module else "",
        map_params(extra_params, "{}"),
        map_params(lib_dirs, '-I"{}"'),
        TARGET + ".vlt",
        map_params(lib_files, '"{}"'),
    )

    return [source_file_issue_action(), action]


@dataclass(frozen=True)
class SimulationConfig:
    """Simulation parameters, for sim and test commands."""

    testbench_name: str  # The testbench name, without the 'v' suffix.
    build_testbench_name: str  # testbench_name prefixed by build dir.
    srcs: List[str]  # List of source files to compile.


def waves_target(
    api_env: ApioEnv,
    name: str,
    vcd_file_target: NodeList,
    sim_config: SimulationConfig,
    allways_build: bool = False,
) -> List[Alias]:
    """Construct a target to launch the QTWave signal viwer.
    vcd_file_target is the simulator target that generated the vcd file
    with the signals. Returns the new targets.
    """

    # -- Construct the commands list.
    commands = []

    # -- On windows we need to setup the cache. This could be done once
    # -- when the oss-cad-suite is installed but since we currently don't
    # -- have a package setup mechanism, we do it here on each invocation.
    # -- The time penalty is negligible.
    # -- With the stock oss-cad-suite windows package, this is done in the
    # -- environment.bat script.
    if api_env.is_windows:
        commands.append("gdk-pixbuf-query-loaders --update-cache")

    # -- The actual wave viewer command.
    commands.append(
        "gtkwave {0} {1} {2}.gtkw".format(
            '--rcvar "splash_disable on" --rcvar "do_initial_zoom_fit 1"',
            vcd_file_target[0],
            sim_config.testbench_name,
        )
    )

    target = api_env.alias(
        name,
        source=vcd_file_target,
        action=commands,
        allways_build=allways_build,
    )

    return target


def check_valid_testbench_name(testbench: str) -> None:
    """Check if a testbench name is valid. If not, print an error message
    and exit."""
    if not is_verilog_src(testbench) or not has_testbench_name(testbench):
        secho_lines(
            ["red"],
            [
                f"Error: '{testbench}' is not a valid testbench file name.",
                TESTBENCH_HINT,
            ],
        )
        sys.exit(1)


def get_sim_config(
    testbench: str,
    synth_srcs: List[str],
    test_srcs: List[str],
) -> SimulationConfig:
    """Returns a SimulationConfig for a sim command. 'testbench' is
    an optional testbench file name. 'synth_srcs' and 'test_srcs' are the
    all the project's synth and testbench files found in the project as
    returne by source_files()."""

    # -- Handle the testbench file selection. The end result is a single
    # -- testbench file name in testbench that we simulate, or a fatal error.
    if testbench:
        # -- Case 1 - Testbench file name is specified in the command or
        # -- apio.ini. Fatal error if invalid.
        check_valid_testbench_name(testbench)
    elif len(test_srcs) == 0:
        # -- Case 2 Testbench name was not specified and no testbench files
        # -- were found in the project.
        secho_lines(
            ["red"],
            [
                "Error: No testbench files found in the project.",
                TESTBENCH_HINT,
            ],
        )
        sys.exit(1)
    elif len(test_srcs) == 1:
        # -- Case 3 Testbench name was not specified but there is exactly
        # -- one in the project.
        testbench = test_srcs[0]
        secho_lines(
            ["cyan"],
            [f"Found testbench file [{testbench}]"],
        )
    else:
        # -- Case 4 Testbench name was not specified and there are multiple
        # -- testbench files in the project.
        secho_lines(
            ["red", "yellow"],
            [
                "Error: Multiple testbench files found in the project.",
                "Please specify the testbench file name in the command "
                "or in apio.ini 'default-testbench' option.",
            ],
        )
        sys.exit(1)

    # -- This should not happen. If it does, it's a programming error.
    assert testbench, "get_sim_config(): Missing testbench file name"

    # -- Construct a SimulationParams with all the synth files + the
    # -- testbench file.
    testbench_name = basename(testbench)
    build_testbench_name = BUILD_DIR_SEP + testbench_name
    srcs = synth_srcs + [testbench]
    return SimulationConfig(testbench_name, build_testbench_name, srcs)


def get_tests_configs(
    testbench: str,
    synth_srcs: List[str],
    test_srcs: list[str],
) -> List[SimulationConfig]:
    """Return a list of SimulationConfigs for each of the testbenches that
    need to be run for a 'apio test' command. If testbench is empty,
    all the testbenches in test_srcs will be tested. Otherwise, only the
    testbench in testbench will be tested. synth_srcs and test_srcs are
    source and test file lists as returned by source_files()."""
    # List of testbenches to be tested.

    # -- Handle the testbench files selection. The end result is a list of one
    # -- or more testbench file names in testbenches that we test.
    if testbench:
        # -- Case 1 - a testbench file name is specified in the command or
        # -- apio.ini. Fatal error if invalid.
        check_valid_testbench_name(testbench)
        testbenches = [testbench]
    elif len(test_srcs) == 0:
        # -- Case 2 - Testbench file name was not specified and there are no
        # -- testbench files in the project.
        secho_lines(
            ["red", "yellow"],
            [
                "Error: No testbench files found in the project.",
                TESTBENCH_HINT,
            ],
        )
        sys.exit(1)
    else:
        # -- Case 3 - Testbench file name was not specified but there are one
        # -- or more testbench files in the project.
        testbenches = test_srcs

    # -- If this fails, it's a programming error.
    assert testbenches, "get_tests_configs(): no testbenches"

    # Construct a config for each testbench.
    configs = []
    for tb in testbenches:
        testbench_name = basename(tb)
        build_testbench_name = BUILD_DIR_SEP + testbench_name
        srcs = synth_srcs + [tb]
        configs.append(
            SimulationConfig(testbench_name, build_testbench_name, srcs)
        )

    return configs


def is_verilog_src(file_name: str) -> bool:
    """Given a file name, determine by its extension if it's a verilog
    source file (testbenches included)."""
    _, ext = os.path.splitext(file_name)
    return ext in SRC_SUFFIXES


def has_testbench_name(file_name: str) -> bool:
    """Given a file name, return true if it's base name indicates a
    testbench. It can be for example abc_tb.v or _build/abc_tb.out.
    The file extension is ignored.
    """
    name, _ = os.path.splitext(file_name)
    return name.lower().endswith("_tb")


def source_file_issue_action() -> FunctionAction:
    """Returns a SCons action that scans the source files and print
    error or warning messages about issues it finds."""

    # A regex to identify "$dumpfile(" in testbenches.
    testbench_dumpfile_re = re.compile(r"[$]dumpfile\s*[(]")

    def report_source_files_issues(
        source: List[File],
        target: List[Alias],
        env: SConsEnvironment,
    ):
        """The scanner function.."""

        _ = (target, env)  # Unused

        for file in source:

            # -- For now we report issues only in testbenches so skip
            # -- otherwise.
            if not is_verilog_src(file.name) or not has_testbench_name(
                file.name
            ):
                continue

            # -- Here the file is a testbench file.
            secho(f"Testbench {file.name}", fg="cyan", bold=True, color=True)

            # -- Read the testbench file text.
            file_text = file.get_text_contents()

            # -- if contains $dumpfile, print a warning.
            if testbench_dumpfile_re.findall(file_text):
                secho(
                    f"Warning: [{file.name}] Using $dumpfile() in apio "
                    "testbenches is not recomanded.",
                    fg="magenta",
                    color=True,
                )

    return Action(report_source_files_issues, "Scanning for issues.")


def source_files(apio_env: ApioEnv) -> Tuple[List[str], List[str]]:
    """Get the list of *.v files, splitted into synth and testbench lists.
    If a .v file has the suffix _tb.v it's is classified st a testbench,
    otherwise as a synthesis file.
    """
    # -- Get a list of all *.v and .sv files in the project dir.
    files: List[File] = apio_env.scons_env.Glob("*.sv")
    if files:
        secho(
            "Warning: project contains .sv files, system-verilog support "
            "is experimental.",
            fg="yellow",
            color=True,
        )
    files = files + apio_env.scons_env.Glob("*.v")

    # Split file names to synth files and testbench file lists
    synth_srcs = []
    test_srcs = []
    for file in files:
        if has_testbench_name(file.name):
            test_srcs.append(file.name)
        else:
            synth_srcs.append(file.name)
    return (synth_srcs, test_srcs)


# pylint: disable=too-many-locals
def _print_pnr_report(
    json_txt: str,
    clk_name_index: int,
    verbose: bool,
) -> None:
    """Accepts the text of the pnr json report and prints it in
    a user friendly way. Used by the 'apio report' command."""
    # -- Json text to tree of Dicts.
    report: Dict[str, any] = json.loads(json_txt)

    # --- Report utilization
    secho("")
    secho("UTILIZATION:", fg="cyan", bold=True, color=True)
    utilization = report["utilization"]
    for resource, vals in utilization.items():
        available = vals["available"]
        used = vals["used"]
        percents = int(100 * used / available)
        fg = "magenta" if used > 0 else None
        secho(
            f"{resource:>20}: {used:5} {available:5} {percents:5}%",
            fg=fg,
            color=True,
        )

    # -- Report max clock speeds.
    # --
    # -- NOTE: As of Oct 2024, some projects do not generate timing
    # -- information and this is being investigated.
    # -- See https://github.com/FPGAwars/icestudio/issues/774 for details.
    secho("")
    secho("CLOCKS:", fg="cyan", bold=True, color=True)
    clocks = report["fmax"]
    if len(clocks) > 0:
        for clk_net, vals in clocks.items():
            # -- Extract clock name from the net name.
            clk_signal = clk_net.split("$")[clk_name_index]

            # -- Report speed.
            max_mhz = vals["achieved"]
            styled_max_mhz = style(f"{max_mhz:7.2f}", fg="magenta")
            secho(f"{clk_signal:>20}: {styled_max_mhz} Mhz max")

    # -- For now we ignore the critical path report in the pnr report and
    # -- refer the user to the pnr verbose output.
    secho("")
    if not verbose:
        secho(
            "Use 'apio report --verbose' for more details.",
            fg="yellow",
            color=True,
        )


def report_action(clk_name_index: int, verbose: bool) -> FunctionAction:
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
        _ = (target, env)  # Unused
        json_file: File = source[0]
        json_txt: str = json_file.get_text_contents()
        _print_pnr_report(json_txt, clk_name_index, verbose)

    return Action(print_pnr_report, "Formatting pnr report.")


def programmer_cmd(apio_env: ApioEnv) -> str:
    """Return the programmer command as derived from the scons "prog"
    arg."""

    # Get the programer command template arg.
    command = apio_env.params.cmds.upload.programmer_cmd

    # If empty then return as is. This must be an apio command that
    # doesn't use the programmer.
    if not command:
        return command

    # It's an error if the programmer command doesn't have the $SOURCE
    # placeholder when scons inserts the binary file name.
    if "$SOURCE" not in command:
        secho(
            "Error: [Internal] $SOURCE is missing in programmer command: "
            f"{command}",
            fg="red",
            color=True,
        )
        sys.exit(1)

    return command


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
def iverilog_action(
    *,
    verbose: bool,
    vcd_output_name: str,
    is_interactive: bool,
    extra_params: List[str] = None,
    lib_dirs: List[str] = None,
    lib_files: List[str] = None,
) -> str:
    """Construct an iverilog scons action string.
    * env: Rhe scons environment.
    * verbose: IVerilog will show extra info.
    * vcd_output_name: Value for the macro VCD_OUTPUT.
    * is_interactive: True for apio sim, False otherwise.
    * extra_params: Optional list of additional IVerilog params.
    * lib_dirs: Optional list of dir pathes to include.
    * lib_files: Optional list of library files to compile.
    *
    * Returns the scons action string for the IVerilog command.
    """

    # Escaping for windows. '\' -> '\\'
    escaped_vcd_output_name = vcd_output_name.replace("\\", "\\\\")

    # -- Construct the action string.
    # -- The -g2012 is for system-verilog support and we use it here as an
    # -- experimental feature.
    action = (
        "iverilog -g2012 {0} -o $TARGET {1} {2} {3} {4} {5} $SOURCES"
    ).format(
        "-v" if verbose else "",
        f"-DVCD_OUTPUT={escaped_vcd_output_name}",
        "-DINTERACTIVE_SIM" if is_interactive else "",
        map_params(extra_params, "{}"),
        map_params(lib_dirs, '-I"{}"'),
        map_params(lib_files, '"{}"'),
    )

    return action


def basename(file_name: str) -> str:
    """Given a file name, returns it with the extension removed."""
    result, _ = os.path.splitext(file_name)
    return result


def vlt_path(path: str) -> str:
    """Normalize a path that is used in the verilator config file
    hardware.vlt. On windows it replaces "\" with "/". Otherwise it
    leaves the path as is.
    """
    return path.replace("\\", "/")


def make_verilator_config_builder(config_lines: List[str]):
    """Create a scons Builder that writes a verilator config file
    (hardware.vlt) with the given text."""

    # -- Join the lines into a single string.
    config_text = "\n".join(config_lines)

    def verilator_config_func(target, source, env):
        """Creates a verilator .vlt config files."""
        _ = (source, env)  # Unused
        with open(target[0].get_path(), "w", encoding="utf-8") as target_file:
            target_file.write(config_text)
        return 0

    return Builder(
        action=Action(
            verilator_config_func, "Creating verilator config file."
        ),
        suffix=".vlt",
    )


def configure_cleanup(apio_env: ApioEnv) -> None:
    """Should be called only when the "clean" target is specified.
    Configures in scons env do delete all the files in the build directory.
    """

    # -- Sanity check.
    assert apio_env.scons_env.GetOption(
        "clean"
    ), "Error, cleaning not requested."

    # -- Get the underlying scons environment.
    scons_env = apio_env.scons_env

    # -- Get the list of all files to clean. Scons adds to the list non
    # -- existing files from other targets it encountered.
    files_to_clean = (
        scons_env.Glob(f"{BUILD_DIR_SEP}*")
        + scons_env.Glob("zadig.ini")
        + scons_env.Glob(".sconsign.dblite")
        + scons_env.Glob("_build")
    )

    # pylint: disable=fixme
    # -- TODO: Remove the cleanup of legacy files after releasing the first
    # -- release with the _build directory.
    # --
    # --
    # -- Until apio 0.9.6, the build artifacts were created in the project
    # -- directory rather than the _build directory. To simplify the
    # -- transition we clean here also left over files from 0.9.5.
    legacy_files_to_clean = (
        scons_env.Glob("hardware.*")
        + scons_env.Glob("*_tb.vcd")
        + scons_env.Glob("*_tb.out")
    )

    if legacy_files_to_clean:
        secho(
            "Deleting also leftover files.",
            fg="yellow",
            color=True,
        )

        files_to_clean.extend(legacy_files_to_clean)

    # -- Create a dummy target.  I
    dummy_target = scons_env.Command("cleanup-target", "", "")

    # -- Associate all the files with the dummy target.
    scons_env.Clean(dummy_target, files_to_clean)
