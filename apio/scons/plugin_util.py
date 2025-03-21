# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Helper functions for apio scons plugins.
"""

# pylint: disable=consider-using-f-string

import sys
import os
import re
import json
from glob import glob
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union
from rich.table import Table
from rich import box
from SCons import Scanner
from SCons.Builder import Builder
from SCons.Action import FunctionAction, Action
from SCons.Node.FS import File
from SCons.Script.SConscript import SConsEnvironment
from SCons.Node import NodeList
from SCons.Node.Alias import Alias
from apio.scons.apio_env import ApioEnv
from apio.common.apio_consts import TARGET, BUILD_DIR
from apio.common.apio_console import cout, cerror, cwarning, cprint
from apio.common.apio_styles import INFO, BORDER, EMPH1, EMPH2, EMPH3


# -- A list with the file extensions of the verilog source files.
SRC_SUFFIXES = [".v", ".sv"]

TESTBENCH_HINT = "Testbench file names must end with '_tb.v' or '_tb.sv'."


def map_params(params: Optional[List[Union[str, Path]]], fmt: str) -> str:
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

    # Convert parmas to stripped strings.
    params = [str(x).strip() for x in params]

    # Drop the empty params and map the rest.
    mapped_params = [fmt.format(x) for x in params if x]

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
        cwarning(f"No {file_ext} constraints file, assuming '{result}'.")
        return result
    # Case 2: Exactly one file found.
    if n == 1:
        result = str(files[0])
        return result
    # Case 3: Multiple matching files.
    cerror(
        f"Found multiple '*{file_ext}' "
        "constrain files, expecting exactly one."
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
                cout(
                    f"Dependency candidate {dependency} does not exist, "
                    "dropping."
                )

        # Sort the strings for determinism.
        dependencies = sorted(list(dependencies))

        # Debug info.
        if apio_env.is_debug:
            cout(f"Dependencies of {file_node.name}:", style=EMPH2)
            for dependency in dependencies:
                cout(f"  {dependency}", style=EMPH2)

        # All done
        return apio_env.scons_env.File(dependencies)

    return apio_env.scons_env.Scanner(function=verilog_src_scanner_func)


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
def verilator_lint_action(
    apio_env: ApioEnv,
    *,
    extra_params: List[str] = None,
    lib_dirs: List[Path] = None,
    lib_files: List[Path] = None,
) -> str:
    """Construct an verilator scons action string.
    * extra_params: Optional additional arguments.
    * libs_dirs: Optional directories for include search.
    * lib_files: Optional additional files to include.
    """

    # -- Sanity checks
    assert apio_env.targeting("lint")
    assert apio_env.params.target.HasField("lint")

    # -- Keep short references.
    params = apio_env.params
    lint_params = params.target.lint

    # -- Determine top module.
    top_module = (
        lint_params.top_module
        if lint_params.top_module
        else params.project.top_module
    )

    # -- Construct the action
    action = (
        "verilator_bin --lint-only --quiet --bbox-unsup --timing "
        "-Wno-TIMESCALEMOD -Wno-MULTITOP "
        "{0} {1} {2} {3} {4} {5} {6} {7} {8} $SOURCES"
    ).format(
        "-Wall" if lint_params.verilator_all else "",
        "-Wno-style" if lint_params.verilator_no_style else "",
        map_params(lint_params.verilator_no_warns, "-Wno-{}"),
        map_params(lint_params.verilator_warns, "-Wwarn-{}"),
        f"--top-module {top_module}",
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
    always_build: bool = False,
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
        always_build=always_build,
    )

    return target


def check_valid_testbench_name(testbench: str) -> None:
    """Check if a testbench name is valid. If not, print an error message
    and exit."""
    if not is_verilog_src(testbench) or not has_testbench_name(testbench):
        cerror(f"'{testbench}' is not a valid testbench file name.")
        cout(TESTBENCH_HINT, style=INFO)
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
        cerror("No testbench files found in the project.")
        cout(TESTBENCH_HINT, style=INFO)

        sys.exit(1)
    elif len(test_srcs) == 1:
        # -- Case 3 Testbench name was not specified but there is exactly
        # -- one in the project.
        testbench = test_srcs[0]
        cout(f"Found testbench file {testbench}", style=EMPH1)
    else:
        # -- Case 4 Testbench name was not specified and there are multiple
        # -- testbench files in the project.
        cerror("Multiple testbench files found in the project.")
        cout(
            "Please specify the testbench file name in the command "
            "or in apio.ini 'default-testbench' option.",
            style=INFO,
        )
        sys.exit(1)

    # -- This should not happen. If it does, it's a programming error.
    assert testbench, "get_sim_config(): Missing testbench file name"

    # -- Construct a SimulationParams with all the synth files + the
    # -- testbench file.
    testbench_name = basename(testbench)
    build_testbench_name = str(BUILD_DIR / testbench_name)
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
        cerror("No testbench files found in the project.")
        cout(TESTBENCH_HINT, style=INFO)
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
        build_testbench_name = str(BUILD_DIR / testbench_name)
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
            cout(f"Testbench {file.name}", style=EMPH1)

            # -- Read the testbench file text.
            file_text = file.get_text_contents()

            # -- if contains $dumpfile, print a warning.
            if testbench_dumpfile_re.findall(file_text):
                cwarning(
                    "Using $dumpfile() in apio "
                    "testbenches is not recomanded."
                )

    return Action(report_source_files_issues, "Scanning for issues.")


# Remove apio_env ark is not needed anymore.
# pylint: disable=unused-argument
def source_files(apio_env: ApioEnv) -> Tuple[List[str], List[str]]:
    """Get the list of *.v|sv files in the directory tree under the current
    directory, splitted into synth and testbench lists.
    If source file has the suffix _tb it's is classified st a testbench,
    otherwise as a synthesis file.
    """
    # -- Get a list of all *.v and .sv files in the project dir.
    # -- Ideally we should use the scons env.Glob() method but it doesn't
    # -- work with the recursive=True option. So we use the glob() function
    # -- instead.
    files: List[str] = glob("**/*.sv", recursive=True)
    if files:
        cwarning(
            "Project contains .sv files, system-verilog support "
            "is experimental."
        )
    files = files + glob("**/*.v", recursive=True)

    # Split file names to synth files and testbench file lists
    synth_srcs = []
    test_srcs = []
    for file in files:
        if has_testbench_name(file):
            test_srcs.append(file)
        else:
            synth_srcs.append(file)
    return (synth_srcs, test_srcs)


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def _print_pnr_utilization_report(report: Dict[str, any]):
    table = Table(
        show_header=True,
        show_lines=False,
        box=box.SQUARE,
        border_style=BORDER,
        title="FPGA Resource Utilization",
        title_justify="left",
        padding=(0, 2),
    )

    # -- Add columns.
    table.add_column("RESOURCE", no_wrap=True)
    table.add_column("USED", no_wrap=True, justify="right")
    table.add_column("TOTAL", no_wrap=True, justify="right")
    table.add_column("UTIL.", no_wrap=True, justify="right")

    # -- Add rows
    utilization = report["utilization"]
    for resource, vals in utilization.items():
        used = vals["used"]
        used_str = f"{used}  " if used else ""
        available = vals["available"]
        available_str = f"{available}  "
        percents = int(100 * used / available)
        percents_str = f"{percents}%  " if used else ""
        style = EMPH3 if used > 0 else None
        table.add_row(
            resource, used_str, available_str, percents_str, style=style
        )

    # -- Render the table
    cout()
    cprint(table)


def _maybe_print_pnr_clocks_report(
    report: Dict[str, any], clk_name_index: int
) -> bool:
    clocks = report["fmax"]
    if len(clocks) == 0:
        return False

    table = Table(
        show_header=True,
        show_lines=True,
        box=box.SQUARE,
        border_style=BORDER,
        title="Clock Information",
        title_justify="left",
        padding=(0, 2),
    )

    # -- Add columns
    table.add_column("CLOCK", no_wrap=True)
    table.add_column(
        "MAX SPEED [Mhz]", no_wrap=True, justify="right", style=EMPH3
    )

    # -- Add rows.
    clocks = report["fmax"]
    for clk_net, vals in clocks.items():
        # -- Extract clock name from the net name.
        clk_signal = clk_net.split("$")[clk_name_index]
        # -- Extract speed
        max_mhz = vals["achieved"]
        # -- Add row.
        table.add_row(clk_signal, f"{max_mhz:.2f}")

    # -- Render the table
    cout()
    cprint(table)
    return True


def _print_pnr_report(
    json_txt: str,
    clk_name_index: int,
    verbose: bool,
) -> None:
    """Accepts the text of the pnr json report and prints it in
    a user friendly way. Used by the 'apio report' command."""
    # -- Parse the json text into a tree of dicts.
    report: Dict[str, any] = json.loads(json_txt)

    # -- Print the utilization table.
    _print_pnr_utilization_report(report)

    # -- Print the optional clocks table.
    clock_report_printed = _maybe_print_pnr_clocks_report(
        report, clk_name_index
    )

    # -- Print summary.
    cout("")
    if not clock_report_printed:
        cout("No clocks were found in the design.", style=INFO)
    if not verbose:
        cout(
            "Run 'apio report --verbose' for more details.",
            nl=False,
            style=INFO,
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


def get_programmer_cmd(apio_env: ApioEnv) -> str:
    """Return the programmer command as derived from the scons "prog"
    arg."""

    # Should be called only if scons paramsm has 'upload' target parmas.
    params = apio_env.params
    assert params.target.HasField("upload"), params

    # Get the programer command template arg.
    programmer_cmd = params.target.upload.programmer_cmd
    assert programmer_cmd, params

    # It's an error if the programmer command doesn't have the $SOURCE
    # placeholder when scons inserts the binary file name.
    if "$SOURCE" not in programmer_cmd:
        cerror(
            "[Internal] $SOURCE is missing in programmer command: "
            f"{programmer_cmd}"
        )
        sys.exit(1)

    return programmer_cmd


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
def iverilog_action(
    *,
    verbose: bool,
    vcd_output_name: str,
    is_interactive: bool,
    extra_params: List[str] = None,
    lib_dirs: List[Path] = None,
    lib_files: List[Path] = None,
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


def make_verilator_config_builder(lib_path: Path):
    """Create a scons Builder that writes a verilator config file
    (hardware.vlt) that supresses warnings in the lib directory."""
    assert isinstance(lib_path, Path), lib_path

    # -- Construct a glob of all library files.
    glob_path = str(lib_path / "*")

    # -- Escape for windows. A single backslash is converted into two.
    glob_str = str(glob_path).replace("\\", "\\\\")

    # -- Generate the files lines.  We supress a union of all the errors we
    # -- encountered in all the architectures.
    lines = ["`verilator_config"]
    for rule in [
        "COMBDLY",
        "WIDTHEXPAND",
        "PINMISSING",
        "ASSIGNIN",
        "WIDTHTRUNC",
        "INITIALDLY",
    ]:
        lines.append(f'lint_off -rule {rule}  -file "{glob_str}"')

    # -- Join the lines into text.
    text = "\n".join(lines) + "\n"

    def verilator_config_func(target, source, env):
        """Creates a verilator .vlt config files."""
        _ = (source, env)  # Unused
        with open(target[0].get_path(), "w", encoding="utf-8") as target_file:
            target_file.write(text)
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
        scons_env.Glob(str(BUILD_DIR / "*"))
        + scons_env.Glob("zadig.ini")
        + scons_env.Glob(".sconsign.dblite")
        + scons_env.Glob(str(BUILD_DIR))
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
        cwarning("Deleting also leftover files.")

        files_to_clean.extend(legacy_files_to_clean)

    # -- Create a dummy target.  I
    dummy_target = scons_env.Command("cleanup-target", "", "")

    # -- Associate all the files with the dummy target.
    scons_env.Clean(dummy_target, files_to_clean)
