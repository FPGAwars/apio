# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2

"""Apio scons plugin for the ice40 architecture."""

# pylint: disable=duplicate-code

from pathlib import Path
from SCons.Script import Builder
from SCons.Builder import BuilderBase
from apio.common.common_util import SRC_SUFFIXES
from apio.scons.apio_env import ApioEnv
from apio.scons.plugin_base import PluginBase, ArchPluginInfo
from apio.scons.plugin_util import (
    verilator_lint_action,
    has_testbench_name,
    announce_testbench_action,
    source_files_issue_scanner_action,
    iverilog_action,
    basename,
    make_verilator_config_builder,
    get_define_flags,
)


class PluginIce40(PluginBase):
    """Apio scons plugin for the ice40 architecture."""

    def __init__(self, apio_env: ApioEnv):
        # -- Call parent constructor.
        super().__init__(apio_env)

        # -- Cache values.
        yosys_path = Path(apio_env.params.environment.yosys_path)
        self.yosys_lib_dir = yosys_path / "ice40"
        self.yosys_lib_file = yosys_path / "ice40" / "cells_sim.v"

    def plugin_info(self) -> ArchPluginInfo:
        """Return plugin specific parameters."""
        return ArchPluginInfo(
            constrains_file_ext=".pcf",
            bin_file_suffix=".bin",
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
            action=(
                'yosys -p "synth_ice40 -top {0} {1} -json $TARGET" {2} {3} '
                "$SOURCES"
            ).format(
                params.apio_env_params.top_module,
                " ".join(params.apio_env_params.yosys_synth_extra_options),
                "" if params.verbosity.all or params.verbosity.synth else "-q",
                get_define_flags(apio_env),
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
            target.append(apio_env.target + ".pnr")
            return target, source

        # -- Create the builder.
        return Builder(
            action=(
                "nextpnr-ice40 --{0} --package {1} --json $SOURCE "
                "--asc $TARGET --report {2} --pcf {3} {4} {5}"
            ).format(
                params.fpga_info.ice40.type,
                params.fpga_info.ice40.pack,
                apio_env.target + ".pnr",
                self.constrain_file(),
                "" if params.verbosity.all or params.verbosity.pnr else "-q",
                " ".join(params.apio_env_params.nextpnr_extra_options),
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

        # -- Sanity checks
        assert apio_env.targeting("sim", "test")
        assert params.target.HasField("sim") or params.target.HasField("test")

        # -- We use a generator because we need a different action
        # -- string for sim and test.
        def action_generator(target, source, env, for_signature):
            _ = (source, env, for_signature)  # Unused
            # Extract testbench name from target file name.
            testbench_file = str(target[0])
            assert has_testbench_name(testbench_file), testbench_file
            testbench_name = basename(testbench_file)

            # Construct the actions list.
            action = [
                # -- Print a testbench title.
                announce_testbench_action(),
                # -- Scan source files for issues.
                source_files_issue_scanner_action(),
                # -- Perform the actual test or sim compilation.
                iverilog_action(
                    apio_env,
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

        # -- Sanity checks
        assert self.apio_env.targeting("lint")

        # -- Make the builder.
        return make_verilator_config_builder(self.yosys_lib_dir)

    # @overrides
    def lint_builder(self) -> BuilderBase:
        """Creates and returns the lint builder."""

        return Builder(
            action=verilator_lint_action(
                self.apio_env,
                extra_params=["-DNO_ICE40_DEFAULT_ASSIGNMENTS"],
                lib_dirs=[self.yosys_lib_dir],
                lib_files=[self.yosys_lib_file],
            ),
            src_suffix=SRC_SUFFIXES,
            source_scanner=self.verilog_src_scanner,
        )
