# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2

"""Apio scons related utilities.."""

import sys
from pathlib import Path
from SCons.Script import ARGUMENTS, COMMAND_LINE_TARGETS
from google.protobuf import text_format
from apio.common.common_util import get_project_source_files
from apio.scons.plugin_ice40 import PluginIce40
from apio.scons.plugin_ecp5 import PluginEcp5
from apio.scons.plugin_gowin import PluginGowin
from apio.common.proto.apio_pb2 import (
    SimParams,
    SconsParams,
    ICE40,
    ECP5,
    GOWIN,
)
from apio.common import apio_console
from apio.scons.apio_env import ApioEnv
from apio.scons.plugin_base import PluginBase
from apio.common import rich_lib_windows
from apio.scons.plugin_util import (
    get_sim_config,
    get_tests_configs,
    gtkwave_target,
    report_action,
    get_programmer_cmd,
)
from apio.common.apio_console import cerror, cout

# -- Scons builders ids.
SYNTH_BUILDER = "SYNTH_BUILDER"
PNR_BUILDER = "PNR_BUILDER"
BITSTREAM_BUILDER = "BITSTREAM_BUILDER"
TESTBENCH_COMPILE_BUILDER = "TESTBENCH_COMPILE_BUILDER"
TESTBENCH_RUN_BUILDER = "TESTBENCH_RUN_BUILDER"
YOSYS_DOT_BUILDER = "YOSYS_DOT_BUILDER"
GRAPHVIZ_RENDERER_BUILDER = "GRAPHVIZ_RENDERER_BUILDER"
LINT_CONFIG_BUILDER = "LINT_CONFIG_BUILDER"
LINT_BUILDER = "LINT_BUILDER"


class SconsHandler:
    """Base apio scons handler"""

    def __init__(self, apio_env: ApioEnv, arch_plugin: PluginBase):
        """Do not call directly, use SconsHandler.start()."""
        self.apio_env = apio_env
        self.arch_plugin = arch_plugin

    @staticmethod
    def start() -> None:
        """This static method is called from SConstruct to create and
        execute an SconsHandler."""

        # -- Read the text of the scons params file.
        params_path = Path(ARGUMENTS["params"])
        with open(params_path, "r", encoding="utf8") as f:
            proto_text = f.read()

        # -- Parse the text into SconsParams object.
        params: SconsParams = text_format.Parse(proto_text, SconsParams())

        # -- Compare the params timestamp to the timestamp in the command.
        timestamp = ARGUMENTS["timestamp"]
        assert params.timestamp == timestamp

        # -- If running on windows, apply the lib library workaround
        if params.environment.is_windows:
            rich_lib_windows.apply_workaround()

        # -- Set terminal mode and theme to match the apio process.
        apio_console.configure(
            terminal_mode=params.environment.terminal_mode,
            theme_name=params.environment.theme_name,
        )

        # -- Create the apio environment.
        apio_env = ApioEnv(COMMAND_LINE_TARGETS, params)

        # -- Select the plugin.
        if params.arch == ICE40:
            plugin = PluginIce40(apio_env)
        elif params.arch == ECP5:
            plugin = PluginEcp5(apio_env)
        elif params.arch == GOWIN:
            plugin = PluginGowin(apio_env)
        else:
            cout(
                f"Apio SConstruct dispatch error: unknown arch [{params.arch}]"
            )
            sys.exit(1)

        # -- Create the handler.
        scons_handler = SconsHandler(apio_env, plugin)

        # -- Invoke the handler. This services the scons request.
        scons_handler.execute()

    def _register_common_targets(self, synth_srcs):
        """Register the common synth, pnr, and bitstream operations which
        are used by a few top level targets.
        """

        apio_env = self.apio_env
        params = apio_env.params
        plugin = self.arch_plugin

        # -- Sanity check
        assert apio_env.targeting("build", "upload", "report")

        # -- Synth builder and target.
        apio_env.builder(SYNTH_BUILDER, plugin.synth_builder())

        synth_target = apio_env.builder_target(
            builder_id=SYNTH_BUILDER,
            target=apio_env.target,
            sources=[synth_srcs],
            always_build=(params.verbosity.all or params.verbosity.synth),
        )

        # -- Place-and-route builder and target
        apio_env.builder(PNR_BUILDER, plugin.pnr_builder())

        pnr_target = apio_env.builder_target(
            builder_id=PNR_BUILDER,
            target=apio_env.target,
            sources=[synth_target, self.arch_plugin.constrain_file()],
            always_build=(params.verbosity.all or params.verbosity.pnr),
        )

        # -- Bitstream builder builder and target
        apio_env.builder(BITSTREAM_BUILDER, plugin.bitstream_builder())

        apio_env.builder_target(
            builder_id=BITSTREAM_BUILDER,
            target=apio_env.target,
            sources=pnr_target,
        )

    def _register_build_target(self, synth_srcs):
        """Register the 'build' target which creates the binary bitstream."""
        apio_env = self.apio_env
        params = apio_env.params
        plugin = self.arch_plugin

        # -- Sanity check
        assert apio_env.targeting("build")

        # -- Register the common targets for synth, pnr, and bitstream.
        self._register_common_targets(synth_srcs)

        # -- Top level "build" target.
        apio_env.alias(
            "build",
            source=apio_env.target + plugin.plugin_info().bin_file_suffix,
            always_build=(
                params.verbosity.all
                or params.verbosity.synth
                or params.verbosity.pnr
            ),
        )

    def _register_upload_target(self, synth_srcs):
        """Register the 'upload' target which upload the binary file
        generated by the bitstream generator."""

        apio_env = self.apio_env
        plugin_info = self.arch_plugin.plugin_info()

        # -- Sanity check
        assert apio_env.targeting("upload")

        # -- Register the common targets for synth, pnr, and bitstream.
        self._register_common_targets(synth_srcs)

        # -- Create the top level 'upload' target.
        apio_env.alias(
            "upload",
            source=apio_env.target + plugin_info.bin_file_suffix,
            action=get_programmer_cmd(apio_env),
            always_build=True,
        )

    def _register_report_target(self, synth_srcs):
        """Registers the 'report' target which a report file from the
        PNR generated .pnr file."""
        apio_env = self.apio_env
        params = apio_env.params
        plugin_info = self.arch_plugin.plugin_info()

        # -- Sanity check
        assert apio_env.targeting("report")

        # -- Register the common targets for synth, pnr, and bitstream.
        self._register_common_targets(synth_srcs)

        # -- Register the top level 'report' target.
        apio_env.alias(
            "report",
            source=apio_env.target + ".pnr",
            action=report_action(
                plugin_info.clk_name_index, params.verbosity.pnr
            ),
            always_build=True,
        )

    def _register_graph_target(
        self,
        synth_srcs,
    ):
        """Registers the 'graph' target which generates a .dot file using
        yosys and renders it using graphviz."""
        apio_env = self.apio_env
        params = apio_env.params
        plugin = self.arch_plugin

        # -- Sanity check
        assert apio_env.targeting("graph")
        assert params.target.HasField("graph")

        # -- Create the .dot generation builder and target.
        apio_env.builder(YOSYS_DOT_BUILDER, plugin.yosys_dot_builder())

        dot_target = apio_env.builder_target(
            builder_id=YOSYS_DOT_BUILDER,
            target=apio_env.graph_target,
            sources=synth_srcs,
            always_build=True,
        )

        # -- Create the rendering builder and target.
        apio_env.builder(
            GRAPHVIZ_RENDERER_BUILDER, plugin.graphviz_renderer_builder()
        )
        graphviz_target = apio_env.builder_target(
            builder_id=GRAPHVIZ_RENDERER_BUILDER,
            target=apio_env.graph_target,
            sources=dot_target,
            always_build=True,
        )

        # -- Create the top level "graph" target.
        apio_env.alias(
            "graph",
            source=graphviz_target,
            always_build=True,
        )

    def _register_lint_target(self, synth_srcs, test_srcs):
        """Registers the 'lint' target which creates a lint configuration file
        and runs the linter."""

        apio_env = self.apio_env
        params = apio_env.params
        plugin = self.arch_plugin

        # -- Sanity check
        assert apio_env.targeting("lint")
        assert params.target.HasField("lint")

        # -- Create the builder and target of the config file creation.
        apio_env.builder(LINT_CONFIG_BUILDER, plugin.lint_config_builder())

        lint_config_target = apio_env.builder_target(
            builder_id=LINT_CONFIG_BUILDER,
            target=apio_env.target,
            sources=[],
        )

        # -- Create the builder and target the lint operation.
        apio_env.builder(LINT_BUILDER, plugin.lint_builder())

        lint_out_target = apio_env.builder_target(
            builder_id=LINT_BUILDER,
            target=apio_env.target,
            sources=synth_srcs + test_srcs,
            extra_dependencies=[lint_config_target],
        )

        # -- Create the top level "lint" target.
        apio_env.alias(
            "lint",
            source=lint_out_target,
            always_build=True,
        )

    def _register_sim_target(self, synth_srcs, test_srcs):
        """Registers the 'sim' targets which compiles and runs the
        simulation of a testbench."""

        apio_env = self.apio_env
        params = apio_env.params
        plugin = self.arch_plugin

        # -- Sanity check
        assert apio_env.targeting("sim")
        assert params.target.HasField("sim")

        # -- Get values.
        sim_params: SimParams = params.target.sim
        testbench = sim_params.testbench  # Optional.

        # -- Collect information for sim.
        sim_config = get_sim_config(apio_env, testbench, synth_srcs, test_srcs)

        # -- Compilation builder and target

        apio_env.builder(
            TESTBENCH_COMPILE_BUILDER, plugin.testbench_compile_builder()
        )

        sim_out_target = apio_env.builder_target(
            builder_id=TESTBENCH_COMPILE_BUILDER,
            target=sim_config.build_testbench_name,
            sources=sim_config.srcs,
            always_build=sim_params.force_sim,
        )

        # -- Simulation builder and target..

        apio_env.builder(TESTBENCH_RUN_BUILDER, plugin.testbench_run_builder())

        sim_vcd_target = apio_env.builder_target(
            builder_id=TESTBENCH_RUN_BUILDER,
            target=sim_config.build_testbench_name,
            sources=[sim_out_target],
            always_build=sim_params,
        )

        # -- The top level "sim" target.
        gtkwave_target(
            apio_env,
            "sim",
            sim_vcd_target,
            sim_config,
            sim_params,
        )

    def _register_test_target(self, synth_srcs, test_srcs):
        """Registers 'test' target and its dependencies. Each testbench
        is tested independently with its own set of sub-targets."""

        apio_env = self.apio_env
        params = apio_env.params
        plugin = self.arch_plugin

        # -- Sanity check
        assert apio_env.targeting("test")
        assert params.target.HasField("test")

        # -- Collect the test related values.
        test_params = params.target.test
        tests_configs = get_tests_configs(
            apio_env, test_params.testbench, synth_srcs, test_srcs
        )

        # -- Create compilation and simulation targets.
        apio_env.builder(
            TESTBENCH_COMPILE_BUILDER, plugin.testbench_compile_builder()
        )
        apio_env.builder(TESTBENCH_RUN_BUILDER, plugin.testbench_run_builder())

        # -- Create targets for each testbench we are testing.
        tests_targets = []
        for test_config in tests_configs:

            # -- Create the compilation target.
            test_out_target = apio_env.builder_target(
                builder_id=TESTBENCH_COMPILE_BUILDER,
                target=test_config.build_testbench_name,
                sources=test_config.srcs,
                always_build=True,
            )

            # -- Create the simulation target.
            test_vcd_target = apio_env.builder_target(
                builder_id=TESTBENCH_RUN_BUILDER,
                target=test_config.build_testbench_name,
                sources=[test_out_target],
                always_build=True,
            )

            # -- Append to the list of targets we need to execute.
            tests_targets.append(test_vcd_target)

        # -- The top level 'test' target.
        apio_env.alias("test", source=tests_targets, always_build=True)

    def execute(self):
        """The entry point of the scons handler. It registers the builders
        and targets for the selected command and scons executes in upon
        return."""

        apio_env = self.apio_env

        # -- Collect the lists of the synthesizable files (e.g. "main.v") and a
        # -- testbench files (e.g. "main_tb.v")
        synth_srcs, test_srcs = get_project_source_files()

        # -- Sanity check that we don't call the scons to do cleanup. This is
        # -- handled directly by the 'apio clean' command.
        assert not apio_env.scons_env.GetOption("clean")

        # -- Get the target, we expect exactly one.
        targets = apio_env.command_line_targets
        assert len(targets) == 1, targets
        target = targets[0]

        # -- Dispatch by target.
        # -- Not using python 'match' statement for  compatibility with
        # -- python 3.9.
        if target == "build":
            self._register_build_target(synth_srcs)

        elif target == "upload":
            self._register_upload_target(synth_srcs)

        elif target == "report":
            self._register_report_target(synth_srcs)

        elif target == "graph":
            self._register_graph_target(synth_srcs)

        elif target == "sim":
            self._register_sim_target(synth_srcs, test_srcs)

        elif target == "test":
            self._register_test_target(synth_srcs, test_srcs)

        elif target == "lint":
            self._register_lint_target(synth_srcs, test_srcs)

        else:
            cerror(f"Unexpected scons target: {target}")
            sys.exit(1)

        # -- Note that so far we just registered builders and target.
        # -- The actual execution is done by scons once this method returns.
