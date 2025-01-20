# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2

"""Apio scons related utilities.."""


from apio.scons.apio_env import ApioEnv, TARGET
from apio.scons.plugin_base import PluginBase
from apio.proto.apio_pb2 import SconsParams
from apio.scons.plugin_util import (
    get_sim_config,
    get_tests_configs,
    waves_target,
    source_files,
    report_action,
    programmer_cmd,
    clean_if_requested,
)

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
        self.apio_env = apio_env
        self.arch_plugin = arch_plugin

    def register_builders(self):
        """Register the builders created by the arch plugin."""
        apio_env = self.apio_env
        plugin = self.arch_plugin

        apio_env.builder(SYNTH_BUILDER, plugin.synth_builder())
        apio_env.builder(PNR_BUILDER, plugin.pnr_builder())
        apio_env.builder(BITSTREAM_BUILDER, plugin.bitstream_builder())
        apio_env.builder(
            TESTBENCH_COMPILE_BUILDER, plugin.testbench_compile_builder()
        )
        apio_env.builder(TESTBENCH_RUN_BUILDER, plugin.testbench_run_builder())
        apio_env.builder(YOSYS_DOT_BUILDER, plugin.yosys_dot_builder())
        apio_env.builder(
            GRAPHVIZ_RENDERER_BUILDER, plugin.graphviz_renderer_builder()
        )
        apio_env.builder(LINT_CONFIG_BUILDER, plugin.lint_config_builder())
        apio_env.builder(LINT_BUILDER, plugin.lint_builder())

    # pylint: disable=too-many-locals
    def register_targets(self):
        """Register the targers. This is architecture independent."""

        apio_env = self.apio_env
        params: SconsParams = apio_env.params
        plugin_info = self.arch_plugin.plugin_info()

        # -- Get a list of the synthesizable files (e.g. "main.v") and a list
        # -- of the testbench files (e.g. "main_tb.v")
        synth_srcs, test_srcs = source_files(apio_env)

        # -- The "build" target and its dependencies.
        synth_target = apio_env.builder_target(
            builder_id=SYNTH_BUILDER,
            target=TARGET,
            sources=[synth_srcs],
            always_build=(params.verbosity.all or params.verbosity.synth),
        )
        pnr_target = apio_env.builder_target(
            builder_id=PNR_BUILDER,
            target=TARGET,
            sources=[synth_target, self.arch_plugin.constrain_file()],
            always_build=(params.verbosity.all or params.verbosity.pnr),
        )
        bin_target = apio_env.builder_target(
            builder_id=BITSTREAM_BUILDER,
            target=TARGET,
            sources=pnr_target,
        )
        apio_env.alias(
            "build",
            source=bin_target,
            allways_build=(
                params.verbosity.all
                or params.verbosity.synth
                or params.verbosity.pnr
            ),
        )

        # -- The "report" target.
        apio_env.alias(
            "report",
            source=TARGET + ".pnr",
            action=report_action(
                plugin_info.clk_name_index, params.verbosity.pnr
            ),
            allways_build=True,
        )

        # -- The "upload" target.
        apio_env.alias(
            "upload",
            source=bin_target,
            action=programmer_cmd(apio_env),
            allways_build=True,
        )

        # -- The 'graph' target and its dependencies.
        dot_target = apio_env.builder_target(
            builder_id=YOSYS_DOT_BUILDER,
            target=TARGET,
            sources=synth_srcs,
            always_build=True,
        )
        graphviz_target = apio_env.builder_target(
            builder_id=GRAPHVIZ_RENDERER_BUILDER,
            target=TARGET,
            sources=dot_target,
            always_build=True,
        )
        apio_env.alias(
            "graph",
            source=graphviz_target,
            allways_build=True,
        )

        # -- The 'sim' target and its dependencies, to simulate and display the
        # -- results of a single testbench.
        if apio_env.targeting("sim"):
            sim_params = params.cmds.sim
            testbench = sim_params.testbench
            assert testbench, "Missing sim testbench"
            sim_config = get_sim_config(testbench, synth_srcs, test_srcs)
            sim_out_target = apio_env.builder_target(
                builder_id=TESTBENCH_COMPILE_BUILDER,
                target=sim_config.build_testbench_name,
                sources=sim_config.srcs,
                always_build=sim_params.force_sim,
            )
            sim_vcd_target = apio_env.builder_target(
                builder_id=TESTBENCH_RUN_BUILDER,
                target=sim_config.build_testbench_name,
                sources=[sim_out_target],
                always_build=sim_params,
            )
            waves_target(
                apio_env,
                "sim",
                sim_vcd_target,
                sim_config,
                allways_build=True,
            )

        # -- The  "test" target and its dependencies, to test one or more
        # -- testbenches.
        if apio_env.targeting("test"):
            test_params = params.cmds.test
            tests_configs = get_tests_configs(
                test_params.testbench, synth_srcs, test_srcs
            )
            tests_targets = []
            for test_config in tests_configs:
                test_out_target = apio_env.builder_target(
                    builder_id=TESTBENCH_COMPILE_BUILDER,
                    target=test_config.build_testbench_name,
                    sources=test_config.srcs,
                    always_build=True,
                )

                test_vcd_target = apio_env.builder_target(
                    builder_id=TESTBENCH_RUN_BUILDER,
                    target=test_config.build_testbench_name,
                    sources=[test_out_target],
                    always_build=True,
                )
                test_target = apio_env.alias(
                    test_config.build_testbench_name,
                    source=[test_vcd_target],
                )
                tests_targets.append(test_target)

            # -- The top 'test' target.
            apio_env.alias("test", source=tests_targets, allways_build=True)

        # -- The "lint" target and its dependencies.
        lint_config_target = apio_env.builder_target(
            builder_id=LINT_CONFIG_BUILDER,
            target=TARGET,
            sources=[],
        )
        lint_out_target = apio_env.builder_target(
            builder_id=LINT_BUILDER,
            target=TARGET,
            sources=synth_srcs + test_srcs,
            extra_dependecies=[lint_config_target],
        )
        apio_env.alias(
            "lint",
            source=lint_out_target,
            allways_build=True,
        )

        # -- Handle the cleanu of the artifact files.
        clean_if_requested(apio_env)

    def execute(self):
        """The entry point of the scons handler."""
        self.register_builders()
        self.register_targets()
