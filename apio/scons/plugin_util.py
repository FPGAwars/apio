# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Helper functions for apio scons plugins."""


from glob import glob
import sys
import os
import re
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Union, Callable
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
from apio.common.proto.apio_pb2 import SimParams
from apio.common.common_util import (
    PROJECT_BUILD_PATH,
    has_testbench_name,
    is_source_file,
)
from apio.common.apio_console import cout, cerror, cwarning, ctable
from apio.common.apio_styles import INFO, BORDER, EMPH1, EMPH2, EMPH3


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


def get_constraint_file(apio_env: ApioEnv, file_ext: str) -> str:
    """Returns the name of the constraint file to use.

    env is the sconstruction environment.

    file_ext is a string with the constrained file extension.
    E.g. ".pcf" for ice40.

    Returns the file name if found or exit with an error otherwise.
    """

    # -- If the user specified a 'constraint-file' in apio.ini then use it.
    user_specified = apio_env.params.apio_env_params.constraint_file

    if user_specified:
        path = Path(user_specified)
        # -- Path should be relative.
        if path.is_absolute():
            cerror(f"Constraint file path is not relative: {user_specified}")
            sys.exit(1)
        # -- Constrain file extension should match the architecture.
        if path.suffix != file_ext:
            cerror(
                f"Constraint file should have the extension '{file_ext}': "
                f"{user_specified}."
            )
            sys.exit(1)
        # -- File should not be under _build
        if PROJECT_BUILD_PATH in path.parents:
            cerror(
                f"Constraint file should not be under {PROJECT_BUILD_PATH}: "
                f"{user_specified}."
            )
            sys.exit(1)
        # -- Path should not contain '..' to avoid traveling outside of the
        # -- project and coming back.
        for part in path.parts:
            if part == "..":
                cerror(
                    f"Constraint file path should not contain '..': "
                    f"{user_specified}."
                )
                sys.exit(1)

        # -- Constrain file looks good.
        return user_specified

    # -- No user specified constraint file, we will try to look for it
    # -- in the project tree.
    glob_files: List[str] = glob(f"**/*{file_ext}", recursive=True)

    # -- Exclude files that are under _build
    filtered_files: List[str] = [
        f for f in glob_files if PROJECT_BUILD_PATH not in Path(f).parents
    ]

    # -- Handle by file count.
    n = len(filtered_files)

    # -- Case 1: No matching constrain files.
    if n == 0:
        cerror(f"No constraint file '*{file_ext}' found.")
        sys.exit(1)

    # -- Case 2: Exactly one constrain file found.
    if n == 1:
        result = str(filtered_files[0])
        return result

    # -- Case 3: Multiple matching constrain files.
    cerror(
        f"Found {n} constraint files '*{file_ext}' "
        "in the project tree, which one to use?"
    )
    cout(
        "Use the apio.ini constraint-file option to specify the desired file.",
        style=INFO,
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

    # A regex to match a verilog include directive.
    # Example
    #   Text:     `include "apio_testing.vh"
    #   Capture:  'apio_testing.vh'
    verilog_include_re = re.compile(r'`\s*include\s+["]([^"]+)["]', re.M)

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
        """Given a [System]Verilog file, scan it and return a list of
        references to other files it depends on. It's not require to report
        dependency on another source file in the project since scons loads
        anyway all the source files in the project.

        Returns a list of files. Dependencies that don't have an existing
        file are ignored and not returned. This is to avoid references in
        commented out code to break scons dependencies.
        """
        _ = env  # Unused

        # Sanity check. Should be called only to scan verilog files. If
        # this fails, this is a programming error rather than a user error.
        assert is_source_file(
            file_node.name
        ), f"Not a src file: {file_node.name}"

        # Get the directory of the file, relative to the project root which is
        # the current working directory. This value is equals to "." if the
        # file is in the project root.
        file_dir: str = file_node.get_dir().get_path()

        # Prepare an empty set of dependencies.
        candidates_raw_set = set()

        # Read the file. This returns [] if the file doesn't exist.
        file_content = file_node.get_text_contents()

        # Get verilog includes references.
        candidates_raw_set.update(verilog_include_re.findall(file_content))

        # Get $readmemh() function references.
        candidates_raw_set.update(readmemh_reference_re.findall(file_content))

        # Get IceStudio references.
        candidates_raw_set.update(icestudio_list_re.findall(file_content))

        # Since we don't know if the dependency's path is relative to the file
        # location or the project root, we try both. We prefer to have high
        # recall of dependencies of high precision, risking at most unnecessary
        # rebuilds.
        candidates_set = candidates_raw_set.copy()
        # If the file is not in the project dir, add a dependency also relative
        # to the project dir.
        if file_dir != ".":
            for raw_candidate in candidates_raw_set:
                candidate: str = os.path.join(file_dir, raw_candidate)
                candidates_set.add(candidate)

        # Add the core dependencies. They are always relative to the project
        # root.
        candidates_set.update(core_dependencies)

        # Filter out candidates that don't have a matching files to prevert
        # breaking the build. This handle for example the case where the
        # file references is in a comment or non reachable code.
        # See also https://stackoverflow.com/q/79302552/15038713
        dependencies = []
        for dependency in candidates_set:
            if Path(dependency).exists():
                dependencies.append(dependency)
            elif apio_env.is_debug(1):
                cout(
                    f"Dependency candidate {dependency} does not exist, "
                    "dropping."
                )

        # Sort the strings for determinism.
        dependencies = sorted(list(dependencies))

        # Debug info.
        if apio_env.is_debug(1):
            cout(f"Dependencies of {file_node}:", style=EMPH2)
            for dependency in dependencies:
                cout(f"  {dependency}", style=EMPH2)

        # All done
        return apio_env.scons_env.File(dependencies)

    return apio_env.scons_env.Scanner(function=verilog_src_scanner_func)


def verilator_lint_action(
    apio_env: ApioEnv,
    *,
    extra_params: List[str] = None,
    lib_dirs: List[Path] = None,
    lib_files: List[Path] = None,
) -> List[
    Callable[
        [
            List[File],
            List[Alias],
            SConsEnvironment,
        ],
        None,
    ]
    | str,
]:
    """Construct an verilator scons action.
    * extra_params: Optional additional arguments.
    * libs_dirs: Optional directories for include search.
    * lib_files: Optional additional files to include.
    Returns an action in a form of a list with two steps, a function to call
    and a string command.
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
        else params.apio_env_params.top_module
    )

    # -- Construct the action
    action = (
        "verilator_bin --lint-only --quiet --bbox-unsup --timing "
        "-Wno-TIMESCALEMOD -Wno-MULTITOP -DAPIO_SIM=0 "
        "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} $SOURCES"
    ).format(
        "-Wall" if lint_params.verilator_all else "",
        "-Wno-style" if lint_params.verilator_no_style else "",
        map_params(lint_params.verilator_no_warns, "-Wno-{}"),
        map_params(lint_params.verilator_warns, "-Wwarn-{}"),
        f"--top-module {top_module}",
        get_define_flags(apio_env),
        map_params(extra_params, "{}"),
        map_params(lib_dirs, '-I"{}"'),
        apio_env.target + ".vlt",
        map_params(lib_files, '"{}"'),
    )

    return [source_files_issue_scanner_action(), action]


@dataclass(frozen=True)
class SimulationConfig:
    """Simulation parameters, for sim and test commands."""

    testbench_name: str  # The testbench name, without the 'v' suffix.
    build_testbench_name: str  # testbench_name prefixed by build dir.
    srcs: List[str]  # List of source files to compile.


def detached_action(api_env: ApioEnv, cmd: List[str]) -> Action:
    """
    Launch the given command, given as a list of tokens, in a detached
    (non blocking) mode.
    """

    def action_func(
        target: List[Alias], source: List[File], env: SConsEnvironment
    ):
        """A call back function to perform the detached command invocation."""

        # -- Make the linter happy
        # pylint: disable=consider-using-with
        _ = (target, source, env)

        # -- NOTE: To debug these Popen operations, comment out the stdout=
        # -- and stderr= lines to see the output and error messages from the
        # -- commands.

        # -- Handle the case of Window.
        if api_env.is_windows:
            creationflags = (
                subprocess.DETACHED_PROCESS
                | subprocess.CREATE_NEW_PROCESS_GROUP
            )
            subprocess.Popen(
                cmd,
                creationflags=creationflags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
                shell=False,
            )
            return 0

        # -- Handle the rest (macOS and Linux)
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=True,
            shell=False,
        )
        return 0

    # -- Create the command display string that will be shown to the user.
    cmd_str: str = subprocess.list2cmdline(cmd)
    display_str: str = "[detached] " + cmd_str

    # -- Create the action and return.
    action = Action(action_func, display_str)
    return action


def gtkwave_target(
    api_env: ApioEnv,
    name: str,
    vcd_file_target: NodeList,
    sim_config: SimulationConfig,
    sim_params: SimParams,
) -> List[Alias]:
    """Construct a target to launch the QTWave signal viewer.
    vcd_file_target is the simulator target that generated the vcd file
    with the signals. Returns the new targets.
    """

    # -- Construct the list of actions.
    actions = []

    if sim_params.no_gtkwave:
        # -- User asked to skip gtkwave. The '@' suppresses the printing
        # -- of the echo command itself.
        actions.append(
            "@echo 'Flag --no-gtkwave was found, skipping GTKWave.'"
        )

    else:
        # -- Normal pase, invoking gtkwave.

        # -- On windows we need to setup the cache. This could be done once
        # -- when the oss-cad-suite is installed but since we currently don't
        # -- have a package setup mechanism, we do it here on each invocation.
        # -- The time penalty is negligible.
        # -- With the stock oss-cad-suite windows package, this is done in the
        # -- environment.bat script.
        if api_env.is_windows:
            actions.append("gdk-pixbuf-query-loaders --update-cache")

        # -- The actual wave viewer command.
        gtkwave_cmd = [
            "gtkwave",
            "--rcvar",
            "splash_disable on",
            "--rcvar",
            "do_initial_zoom_fit 1",
            str(vcd_file_target[0]),
            sim_config.testbench_name + ".gtkw",
        ]

        # -- Handle the case where gtkwave is run as a detached app, not
        # -- waiting for it to close and not showing its output.
        if sim_params.detach_gtkwave:
            gtkwave_action = detached_action(api_env, gtkwave_cmd)
        else:
            gtkwave_action = subprocess.list2cmdline(gtkwave_cmd)

        actions.append(gtkwave_action)

    # -- Define a target with the action(s) we created.
    target = api_env.alias(
        name,
        source=vcd_file_target,
        action=actions,
        always_build=True,
    )

    return target


def check_valid_testbench_name(testbench: str) -> None:
    """Check if a testbench name is valid. If not, print an error message
    and exit."""
    if not is_source_file(testbench) or not has_testbench_name(testbench):
        cerror(f"'{testbench}' is not a valid testbench file name.")
        cout(TESTBENCH_HINT, style=INFO)
        sys.exit(1)


def get_sim_config(
    apio_env: ApioEnv,
    testbench: str,
    synth_srcs: List[str],
    test_srcs: List[str],
) -> SimulationConfig:
    """Returns a SimulationConfig for a sim command. 'testbench' is
    an optional testbench file name. 'synth_srcs' and 'test_srcs' are the
    all the project's synth and testbench files found in the project as
    returned by get_project_source_files()."""

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
    build_testbench_name = str(apio_env.env_build_path / testbench_name)
    srcs = synth_srcs + [testbench]
    return SimulationConfig(testbench_name, build_testbench_name, srcs)


def get_tests_configs(
    apio_env: ApioEnv,
    testbench: str,
    synth_srcs: List[str],
    test_srcs: list[str],
) -> List[SimulationConfig]:
    """Return a list of SimulationConfigs for each of the testbenches that
    need to be run for a 'apio test' command. If testbench is empty,
    all the testbenches in test_srcs will be tested. Otherwise, only the
    testbench in testbench will be tested. synth_srcs and test_srcs are
    source and test file lists as returned by get_project_source_files()."""
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
        build_testbench_name = str(apio_env.env_build_path / testbench_name)
        srcs = synth_srcs + [tb]
        configs.append(
            SimulationConfig(testbench_name, build_testbench_name, srcs)
        )

    return configs


def announce_testbench_action() -> FunctionAction:
    """Returns an action that prints a title with the testbench name."""

    def announce_testbench(
        target: List[Alias],
        source: List[File],
        env: SConsEnvironment,
    ):
        """The action function."""
        _ = (target, env)  # Unused

        # -- We expect to find exactly one testbench.
        testbenches = [
            file
            for file in source
            if (is_source_file(file.name) and has_testbench_name(file.name))
        ]
        assert len(testbenches) == 1, testbenches

        # -- Announce it.
        cout()
        cout(f"Testbench {testbenches[0]}", style=EMPH3)

    # -- Run the action but don't announce the action.
    return Action(announce_testbench, strfunction=None)


def source_files_issue_scanner_action() -> FunctionAction:
    """Returns a SCons action that scans the source files and print
    error or warning messages about issues it finds."""

    # A regex to identify "$dumpfile(" in testbenches.
    testbench_dumpfile_re = re.compile(r"[$]dumpfile\s*[(]")

    # A regex to identify "INTERACTIVE_SIM" in testbenches
    interactive_sim_re = re.compile(r"INTERACTIVE_SIM")

    def report_source_files_issues(
        target: List[Alias],
        source: List[File],
        env: SConsEnvironment,
    ):
        """The scanner function."""

        _ = (target, env)  # Unused

        for file in source:

            # -- For now we report issues only in testbenches so skip
            # -- otherwise.
            if not is_source_file(file.name) or not has_testbench_name(
                file.name
            ):
                continue

            # -- Read the testbench file text.
            file_text = file.get_text_contents()

            # -- if contains $dumpfile, print a warning.
            if testbench_dumpfile_re.findall(file_text):
                cwarning("Avoid using $dumpfile() in Apio testbenches.")

            # -- if contains $dumpfile, print a warning.
            if interactive_sim_re.findall(file_text):
                cwarning(
                    "The Apio macro `INTERACTIVE_SIM is deprecated. "
                    "Use `APIO_SIM (0 or 1) instead."
                )

    # -- Run the action but don't announce the action. We will print
    # -- ourselves in report_source_files_issues.
    return Action(report_source_files_issues, strfunction=None)


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
    ctable(table)


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
    ctable(table)
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
        cout("Run 'apio report --verbose' for more details.", style=INFO)


def report_action(clk_name_index: int, verbose: bool) -> FunctionAction:
    """Returns a SCons action to format and print the PNR reort from the
    PNR json report file. Used by the 'apio report' command.
    'script_id' identifies the calling SConstruct script and 'verbose'
    indicates if the --verbose flag was invoked."""

    def print_pnr_report(
        target: List[Alias],
        source: List[File],
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

    # -- [NOTE] Generally speaking we would expect the command to include
    # -- $SOURCE for the binary file path but since we allow custom commands
    # -- using apio.ini's 'programmer-cmd' option, we don't check for it here.

    return programmer_cmd


def get_define_flags(apio_env: ApioEnv) -> str:
    """Return a string with the -D flags for the verilog defines. Returns
    an empty string if there are no defines."""
    flags: List[str] = []
    for define in apio_env.params.apio_env_params.defines:
        flags.append("-D" + define)

    return " ".join(flags)


def iverilog_action(
    apio_env: ApioEnv,
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

    # pylint: disable=too-many-arguments

    # Escaping for windows. '\' -> '\\'
    escaped_vcd_output_name = vcd_output_name.replace("\\", "\\\\")

    # -- Construct the action string.
    # -- The -g2012 is for system-verilog support.
    action = (
        "iverilog -g2012 {0} -o $TARGET {1} {2} {3} {4} {5} {6} {7} $SOURCES"
    ).format(
        "-v" if verbose else "",
        f"-DVCD_OUTPUT={escaped_vcd_output_name}",
        get_define_flags(apio_env),
        f"-DAPIO_SIM={int(is_interactive)}",
        # 'INTERACTIVE_SIM is deprecated and will go away.
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
    (hardware.vlt) that suppresses warnings in the lib directory."""
    assert isinstance(lib_path, Path), lib_path

    # -- Construct a glob of all library files.
    glob_path = str(lib_path / "*")

    # -- Escape for windows. A single backslash is converted into two.
    glob_str = str(glob_path).replace("\\", "\\\\")

    # -- Generate the files lines.  We suppress a union of all the errors we
    # -- encountered in all the architectures.
    lines = ["`verilator_config"]
    for rule in [
        "COMBDLY",
        "WIDTHEXPAND",
        "SPECIFYIGN",
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
