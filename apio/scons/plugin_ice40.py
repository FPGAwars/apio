# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2

"""Apio scons plugin for the ice40 architecture."""

# R0801: Similar lines
# pylint: disable=R0801

from SCons.Script import Builder
from SCons.Builder import BuilderBase
from apio.scons.apio_env import ApioEnv, TARGET
from apio.scons.plugin_base import PluginBase, ArchPluginInfo
from apio.scons.plugin_util import (
    SRC_SUFFIXES,
    verilator_lint_action,
    has_testbench_name,
    source_file_issue_action,
    iverilog_action,
    basename,
    vlt_path,
    make_verilator_config_builder,
)


# pylint: disable=consider-using-f-string
class PluginIce40(PluginBase):
    """Apio scons plugin for the ice40 architecture."""

    def __init__(self, apio_env: ApioEnv):
        # -- Call parent constructor.
        super().__init__(apio_env)

        # -- Cache values.
        self.yosys_lib_dir = apio_env.params.envrionment.yosys_path + "/ice40"
        self.yosys_lib_file = self.yosys_lib_dir + "/cells_sim.v"

    def plugin_info(self) -> ArchPluginInfo:
        """Return plugin specific parameters."""
        return ArchPluginInfo(
            constrains_file_ext=".pcf",
            clk_name_index=0,
        )

    # @overrides
    def synth_builder(self) -> BuilderBase:
        """Creates and returns the synth builder."""
        # -- Keep short references.
        apio_env = self.apio_env
        params = apio_env.params

        # -- The yosys synth builder.
        return Builder(
            action='yosys -p "synth_ice40 -top {0} -json $TARGET" {1} '
            "$SOURCES".format(
                params.project.top_module,
                "" if params.verbosity.all or params.verbosity.synth else "-q",
            ),
            suffix=".json",
            src_suffix=SRC_SUFFIXES,
            source_scanner=self.verilog_src_scanner,
        )

    # @overrides
    def pnr_builder(self) -> BuilderBase:
        """Creates and returns the pnr builder."""
        # -- Keep short references.
        apio_env = self.apio_env
        params = apio_env.params

        # -- We use an emmiter to add to the builder a second output file.
        def emitter(target, source, env):
            _ = env  # Unused
            target.append(TARGET + ".pnr")
            return target, source

        # -- Create the builder.
        return Builder(
            action=(
                "nextpnr-ice40 --{0} --package {1} --json $SOURCE "
                "--asc $TARGET --report {2} --pcf {3} {4}"
            ).format(
                params.fpga_info.ice40.type,
                params.fpga_info.ice40.pack,
                TARGET + ".pnr",
                self.constrain_file(),
                "" if params.verbosity.all or params.verbosity.pnr else "-q",
            ),
            suffix=".asc",
            src_suffix=".json",
            emitter=emitter,
        )

    # @overrides
    def bitstream_builder(self) -> BuilderBase:
        """Creates and returns the bitstream builder."""
        return Builder(
            action="icepack $SOURCE $TARGET",
            suffix=".bin",
            src_suffix=".asc",
        )

    # @overrides
    def testbench_compile_builder(self) -> BuilderBase:
        """Creates and returns the testbench compile builder."""
        # -- Keep short references.
        apio_env = self.apio_env
        params = apio_env.params

        # -- We use a generator because we need a different action
        # -- string for sim and test.
        def action_generator(source, target, env, for_signature):
            _ = (source, env, for_signature)  # Unused
            # Extract testbench name from target file name.
            testbench_file = str(target[0])
            assert has_testbench_name(testbench_file), testbench_file
            testbench_name = basename(testbench_file)

            # Construct the actions list.
            action = [
                # -- Scan source files for issues.
                source_file_issue_action(),
                # -- Perform the actual test or sim compilation.
                iverilog_action(
                    verbose=params.verbosity.all,
                    vcd_output_name=testbench_name,
                    is_interactive=apio_env.targeting("sim"),
                    extra_params=["-DNO_ICE40_DEFAULT_ASSIGNMENTS"],
                    lib_dirs=[self.yosys_lib_dir],
                    lib_files=[self.yosys_lib_file],
                ),
            ]
            return action

        # -- The testbench compiler builder.
        return Builder(
            # -- Dynamic action string generator.
            generator=action_generator,
            suffix=".out",
            src_suffix=SRC_SUFFIXES,
            source_scanner=self.verilog_src_scanner,
        )

    # @overrides
    def lint_config_builder(self) -> BuilderBase:
        """Creates and returns the lint config builder."""
        yosys_vlt_path = vlt_path(self.yosys_lib_dir)
        return make_verilator_config_builder(
            [
                "`verilator_config",
                f'lint_off -rule COMBDLY     -file "{yosys_vlt_path}/*"',
                f'lint_off -rule WIDTHEXPAND -file "{yosys_vlt_path}/*"',
            ]
        )

    # @overrides
    def lint_builder(self) -> BuilderBase:
        """Creates and returns the lint builder."""
        # -- Keep short references.
        apio_env = self.apio_env
        params = apio_env.params
        lint_params = params.target.lint

        top_module = (
            lint_params.top_module
            if lint_params.top_module
            else params.project.top_module
        )

        return Builder(
            action=verilator_lint_action(
                warnings_all=lint_params.verilator_all,
                warnings_no_style=lint_params.verilator_no_style,
                no_warns=lint_params.verilator_no_warns,
                warns=lint_params.verilator_warns,
                top_module=top_module,
                extra_params=["-DNO_ICE40_DEFAULT_ASSIGNMENTS"],
                lib_dirs=[self.yosys_lib_dir],
                lib_files=[self.yosys_lib_file],
            ),
            src_suffix=SRC_SUFFIXES,
            source_scanner=self.verilog_src_scanner,
        )
