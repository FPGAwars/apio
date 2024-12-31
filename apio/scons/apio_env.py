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
from pathlib import Path
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
from SCons.Action import FunctionAction, Action
from SCons.Builder import Builder
from SCons.Environment import BuilderWrapper
import SCons.Defaults


# -- All the build files and other artifcats are created in this this
# -- subdirectory.
BUILD_DIR = "_build"

# -- A shortcut with '/' or '\' appended to the build dir name.
BUILD_DIR_SEP = BUILD_DIR + os.sep

# -- Target name. This is the base file name for various build artifacts.
TARGET = BUILD_DIR_SEP + "hardware"

SUPPORTED_GRAPH_TYPES = ["svg", "pdf", "png"]


class SconsArch(Enum):
    """Identifies the SConstruct script that is running. Used to select
    the desired behavior when it's script dependent."""

    ICE40 = 1
    ECP5 = 2
    GOWIN = 3


@dataclass(frozen=True)
class SimulationConfig:
    """Simulation parameters, for sim and test commands."""

    testbench_name: str  # The testbench name, without the 'v' suffix.
    build_testbench_name: str  # testbench_name prefixed by build dir.
    srcs: List[str]  # List of source files to compile.


# pylint: disable=too-many-public-methods
class ApioEnv:
    """Provides abstracted scons env and other user services."""

    def __init__(self, sconstruct_id: SconsArch, scons_args: Dict[str, str]):
        self.env = SConsEnvironment(ENV=os.environ, tools=[])
        self.sconstruct_id = sconstruct_id
        self.args = scons_args

        # -- Since we ae not using the default environment, make sure it was
        # -- not used unintentionally, e.v. in tests that run create multiple
        # -- scons env in the same session.
        # --
        # pylint: disable=protected-access
        assert (
            SCons.Defaults._default_env is None
        ), "DefaultEnvironment already exists"
        # pylint: enable=protected-access

        # -- Parse debug arg. It's optional.
        val = self.args.get("debug", "False")
        self.is_debug = {"True": True, "False": False}[val]

        # -- Determine if we run on windows. Platform_id is a required arg.
        val = self.args["platform_id"]
        self.is_windows = "windows" in val.lower()

        # Extra info for debugging.
        if self.is_debug:
            self.dump_env_vars()

    def builder(self, builder_id: str, builder):
        """Append to the scons env a builder with given id. The env
        adds it to the BUILDERS dict and also adds to itself an attribute with
        that name that contains a wrapper to that builder."""
        self.env.Append(BUILDERS={builder_id: builder})

    def builder_target(
        self,
        *,
        builder_id: str,
        target,
        sources: List,
        always_build: bool = False,
    ):
        """Creates an return a target that uses the builder with given id."""
        builder_wrapper: BuilderWrapper = getattr(self.env, builder_id)
        target = builder_wrapper(target, sources)
        if always_build:
            self.env.AlwaysBuild(target)
        return target

    def alias(self, name, *, source, action=None, allways_build: bool = False):
        """Creates a target with given dependencies"""
        target = self.env.Alias(name, source, action)
        if allways_build:
            self.env.AlwaysBuild(target)
        return target

    def depends(self, target, dependency):
        """Adds a dependency of one target on another."""
        self.env.Depends(target, dependency)

    def map_params(self, params: Optional[List[str]], fmt: str) -> str:
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

    def basename(self, file_name: str) -> str:
        """Given a file name, returns it with the extension removed."""
        result, _ = os.path.splitext(file_name)
        return result

    def is_verilog_src(
        self, file_name: str, *, include_sv: bool = True
    ) -> bool:
        """Given a file name, determine by its extension if it's a verilog
        source file (testbenches included).  If include_sv is True, include
        also system verilog files."""
        _, ext = os.path.splitext(file_name)
        if include_sv:
            return ext in [".v", ".sv"]
        return ext in [".v"]

    def has_testbench_name(self, file_name: str) -> bool:
        """Given a file name, return true if it's base name indicates a
        testbench. It can be for example abc_tb.v or _build/abc_tb.out.
        The file extension is ignored.
        """
        name, _ = os.path.splitext(file_name)
        return name.lower().endswith("_tb")

    def _dump_parsed_arg(self, name, value, from_default: bool) -> None:
        """Used to dump parsed scons arg. For debugging only."""
        type_name = type(value).__name__
        default = "(default)" if from_default else ""
        self.msg(
            f"Arg  {name:15} ->  {str(value):15} " f"{type_name:6} {default}"
        )

    def arg_bool(self, name: str, default: bool) -> bool:
        """Parse and return a boolean arg."""
        assert (
            isinstance(default, bool) or default is None
        ), f"{name}: {default}"
        # args = get_args(env)
        raw_value = self.args.get(name, None)
        if raw_value is None:
            value = default
        else:
            value = {"True": True, "False": False, True: True, False: False}[
                raw_value
            ]
            if value is None:
                self.fatal_error(
                    f"Invalid boolean argument '{name} = '{raw_value}'."
                )
        # -- Dump if requested.
        if self.is_debug:
            self._dump_parsed_arg(name, value, from_default=raw_value is None)
        return value

    def arg_str(self, name: str, default: str) -> str:
        """Parse and return a string arg."""
        assert (
            isinstance(default, str) or default is None
        ), f"{name}: {default}"
        # args = get_args(env)
        raw_value = self.args.get(name, None)
        value = default if raw_value is None else raw_value
        if self.is_debug:
            self._dump_parsed_arg(name, value, from_default=raw_value is None)
        return value

    def msg(self, text: str, fg: str = None) -> None:
        """Print a message to the user. Similar to click.secho but with
        proper color enforcement. We force colors through the pipe to
        the apio process. If apio itself is pipled out, it's click library
        will strip out the color info.
        """
        reset = fg is not None
        click.secho(text, fg=fg, color=True, reset=reset)

    def info(self, text: str) -> None:
        """Prints a short info message and continue."""
        self.msg(f"Info: {text}")

    def warning(self, text: str) -> None:
        """Prints a short warning message and continue."""
        self.msg(f"Warning: {text}", fg="yellow")

    def error(self, text: str) -> None:
        """Prints a short error message and continue."""
        self.msg(f"Error: {text}", fg="red")

    def fatal_error(self, text: str) -> NoReturn:
        """Prints a short error message and exit with an error code."""
        self.error(text)
        self.env.Exit(1)

    def get_constraint_file(self, file_ext: str, top_module: str) -> str:
        """Returns the name of the constrain file to use.

        env is the sconstrution environment.

        file_ext is a string with the constrained file extension.
        E.g. ".pcf" for ice40.

        top_module is the top module name. It's is used to construct the
        default file name.

        Returns the file name if found or a default name otherwise otherwise.
        """
        # Files in alphabetical order.
        files = self.env.Glob(f"*{file_ext}")
        n = len(files)
        # Case 1: No matching files.
        if n == 0:
            result = f"{top_module.lower()}{file_ext}"
            self.warning(
                f"No {file_ext} constraints file, assuming '{result}'."
            )
            return result
        # Case 2: Exactly one file found.
        if n == 1:
            result = str(files[0])
            return result
        # Case 3: Multiple matching files.
        self.fatal_error(
            f"Found multiple '*{file_ext}' constrain files, expecting one."
        )

    def dump_env_vars(self) -> None:
        """Prints a list of the environment variables. For debugging."""
        dictionary = self.env.Dictionary()
        keys = list(dictionary.keys())
        keys.sort()
        click.secho()
        self.msg(">>> Env vars BEGIN", fg="magenta")
        for key in keys:
            print(f"{key} = {self.env[key]}")
        self.msg("<<< Env vars END\n", fg="magenta")

    def programmer_cmd(self) -> str:
        """Return the programmer command as derived from the scons "prog"
        arg."""

        # Get the programer command template arg.
        prog_arg = self.arg_str("prog", "")

        # If empty then return as is. This must be an apio command that
        # doesn't use the programmer.
        if not prog_arg:
            return prog_arg

        # It's an error if the programmer command doesn't have the $SOURCE
        # placeholder when scons inserts the binary file name.
        if "$SOURCE" not in prog_arg:
            self.fatal_error(
                "[Internal] 'prog' argument does not contain "
                f"the '$SOURCE' marker. [{prog_arg}]",
            )

        return prog_arg

    def source_file_issue_action(self) -> FunctionAction:
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

            for file in source:

                # -- For now we report issues only in testbenches so skip
                # -- otherwise.
                if not self.is_verilog_src(
                    file.name
                ) or not self.has_testbench_name(file.name):
                    continue

                # -- Read the testbench file text.
                file_text = file.get_text_contents()

                # -- if contains $dumpfile, print a warning.
                if testbench_dumpfile_re.findall(file_text):
                    self.msg(
                        f"Warning: [{file.name}] Using $dumpfile() in apio "
                        "testbenches is not recomanded.",
                        fg="magenta",
                    )

        return Action(report_source_files_issues, "Scanning for issues.")

    def verilog_src_scanner(self) -> Scanner.Base:
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
            "boards.json",
            "fpgas.json",
            "programmers.json",
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
            # Sanity check. Should be called only to scan verilog files. If
            # this fails, this is a programming error rather than a user error.
            assert self.is_verilog_src(
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
                elif self.is_debug:
                    self.msg(
                        f"Dependency candidate {dependency} does not exist, "
                        "droping.",
                    )

            # Sort the strings for determinism.
            dependencies = sorted(list(dependencies))

            # Debug info.
            if self.is_debug:
                self.msg(f"Dependencies of {file_node.name}:", fg="blue")
                for dependency in dependencies:
                    self.msg(f"  {dependency}", fg="blue")

            # All done
            return self.env.File(dependencies)

        return self.env.Scanner(function=verilog_src_scanner_func)

    def vlt_path(self, path: str) -> str:
        """Normalize a path that is used in the verilator config file
        hardware.vlt. On windows it replaces "\" with "/". Otherwise it
        leaves the path as is.
        """
        return path.replace("\\", "/")

    def make_verilator_config_builder(self, config_text: str):
        """Create a scons Builder that writes a verilator config file
        (hardware.vlt) with the given text."""

        def verilator_config_func(target, source, env):
            """Creates a verilator .vlt config files."""
            with open(
                target[0].get_path(), "w", encoding="utf-8"
            ) as target_file:
                target_file.write(config_text)
            return 0

        return Builder(
            action=Action(
                verilator_config_func, "Creating verilator config file."
            ),
            suffix=".vlt",
        )

    def dot_builder(
        self,
        *,
        top_module: str,
        verilog_src_scanner,
        verbose: bool,
    ):
        """Creates and returns an SCons dot builder that generates the graph
        in .dot format.

        'verilog_src_scanner' is a verilog file scanner that identify
        additional dependencies for the build, for example, icestudio
        propriety includes.
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

    def graphviz_builder(
        self,
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
            self.msg(f"Generated {TARGET}.{graph_type}", fg="green")

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

    def source_files(self) -> Tuple[List[str], List[str]]:
        """Get the list of *.v files, splitted into synth and testbench lists.
        If a .v file has the suffix _tb.v it's is classified st a testbench,
        otherwise as a synthesis file.
        """
        # -- Get a list of all *.v and .sv files in the project dir.
        files: List[File] = self.env.Glob("*.sv")
        if files:
            self.msg(
                "Warning: project contains .sv files, system-verilog support "
                "is experimental.",
                fg="yellow",
            )
        files = files + self.env.Glob("*.v")

        # Split file names to synth files and testbench file lists
        synth_srcs = []
        test_srcs = []
        for file in files:
            if self.has_testbench_name(file.name):
                test_srcs.append(file.name)
            else:
                synth_srcs.append(file.name)
        return (synth_srcs, test_srcs)

    def get_sim_config(
        self, testbench: str, synth_srcs: List[str]
    ) -> SimulationConfig:
        """Returns a SimulationConfig for a sim command. 'testbench' is
        a required testbench file name. 'synth_srcs' is the list of all
        module sources as returned by get_source_files()."""
        # Apio sim requires a testbench arg so ifi this missing here, it's a
        # programming error.
        if not testbench:
            self.fatal_error("[Internal] Sim testbench name got lost.")

        # Construct a SimulationParams with all the synth files + the
        # testbench file.
        testbench_name = self.basename(testbench)
        build_testbench_name = BUILD_DIR_SEP + testbench_name
        srcs = synth_srcs + [testbench]
        return SimulationConfig(testbench_name, build_testbench_name, srcs)

    def get_tests_configs(
        self,
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
            testbenches = [testbench]
        else:
            testbenches = test_srcs

        # If there are not testbenches, we consider the test as failed.
        if len(testbenches) == 0:
            self.fatal_error("No testbench files found (*_tb.v).")

        # Construct a config for each testbench.
        configs = []
        for tb in testbenches:
            testbench_name = self.basename(tb)
            build_testbench_name = BUILD_DIR_SEP + testbench_name
            srcs = synth_srcs + [tb]
            configs.append(
                SimulationConfig(testbench_name, build_testbench_name, srcs)
            )

        return configs

    def waves_target(
        self,
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
        if self.is_windows:
            commands.append("gdk-pixbuf-query-loaders --update-cache")

        # -- The actual wave viewer command.
        commands.append(
            "gtkwave {0} {1} {2}.gtkw".format(
                '--rcvar "splash_disable on" --rcvar "do_initial_zoom_fit 1"',
                vcd_file_target[0],
                sim_config.testbench_name,
            )
        )

        target = self.alias(
            name,
            source=vcd_file_target,
            action=commands,
            allways_build=allways_build,
        )

        return target

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def iverilog_action(
        self,
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
            self.map_params(extra_params, "{}"),
            self.map_params(lib_dirs, '-I"{}"'),
            self.map_params(lib_files, '"{}"'),
        )

        return action

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def verilator_lint_action(
        self,
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
            self.map_params(no_warns, "-Wno-{}"),
            self.map_params(warns, "-Wwarn-{}"),
            f"--top-module {top_module}" if top_module else "",
            self.map_params(extra_params, "{}"),
            self.map_params(lib_dirs, '-I"{}"'),
            TARGET + ".vlt",
            self.map_params(lib_files, '"{}"'),
        )

        return [self.source_file_issue_action(), action]

    # pylint: disable=too-many-locals
    def _print_pnr_report(
        self,
        json_txt: str,
        verbose: bool,
    ) -> None:
        """Accepts the text of the pnr json report and prints it in
        a user friendly way. Used by the 'apio report' command."""
        # -- Json text to tree of Dicts.
        report: Dict[str, any] = json.loads(json_txt)

        # --- Report utilization
        self.msg("")
        self.msg("UTILIZATION:", fg="cyan")
        utilization = report["utilization"]
        for resource, vals in utilization.items():
            available = vals["available"]
            used = vals["used"]
            percents = int(100 * used / available)
            fg = "magenta" if used > 0 else None
            self.msg(
                f"{resource:>20}: {used:5} {available:5} {percents:5}%", fg=fg
            )

        # -- Report max clock speeds.
        # --
        # -- NOTE: As of Oct 2024, some projects do not generate timing
        # -- information and this is being investigated.
        # -- See https://github.com/FPGAwars/icestudio/issues/774 for details.
        self.msg("")
        self.msg("CLOCKS:", fg="cyan")
        clocks = report["fmax"]
        if len(clocks) > 0:
            for clk_net, vals in clocks.items():
                # pylint: disable=fixme
                # TODO: Confirm clk name extraction for Gowin.
                # Extract clock name from the net name.
                if self.sconstruct_id == SconsArch.ECP5:
                    # E.g. '$glbnet$CLK$TRELLIS_IO_IN' -> 'CLK'
                    clk_signal = clk_net.split("$")[2]
                else:
                    # E.g. 'vclk$SB_IO_IN_$glb_clk' -> 'vclk'
                    clk_signal = clk_net.split("$")[0]
                # Report speed.
                max_mhz = vals["achieved"]
                styled_max_mhz = click.style(f"{max_mhz:7.2f}", fg="magenta")
                self.msg(f"{clk_signal:>20}: {styled_max_mhz} Mhz max")

        # -- For now we ignore the critical path report in the pnr report and
        # -- refer the user to the pnr verbose output.
        self.msg("")
        if not verbose:
            self.msg(
                "Use 'apio report --verbose' for more details.", fg="yellow"
            )

    def report_action(self, verbose: bool) -> FunctionAction:
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
            unused(target, env)
            json_file: File = source[0]
            json_txt: str = json_file.get_text_contents()
            self._print_pnr_report(json_txt, verbose)

        return Action(print_pnr_report, "Formatting pnr report.")

    def set_up_cleanup(self) -> None:
        """Should be called only when the "clean" target is specified.
        Configures in scons env do delete all the files in the build directory.
        """

        # -- Should be called only when the 'clean' target is specified.
        # -- If this fails, this is a programming error and not a user error.
        assert self.env.GetOption("clean"), "Option 'clean' is missing."

        # -- Get the list of all files to clean. Scons adds to the list non
        # -- existing files from other targets it encountered.
        files_to_clean = (
            self.env.Glob(f"{BUILD_DIR_SEP}*")
            + self.env.Glob("zadig.ini")
            + self.env.Glob(".sconsign.dblite")
            + self.env.Glob("_build")
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
            self.env.Glob("hardware.*")
            + self.env.Glob("*_tb.vcd")
            + self.env.Glob("*_tb.out")
        )

        if legacy_files_to_clean:
            self.msg(
                "Deleting also left-over files from previous release.",
                fg="yellow",
            )

            files_to_clean.extend(legacy_files_to_clean)

        # -- Create a dummy target.  I
        dummy_target = self.env.Command("cleanup-target", "", "")

        # -- Associate all the files with the dummy target.
        self.env.Clean(dummy_target, files_to_clean)


def unused(*_):
    """Fake a use of an unused variable or argument."""
    # pass
