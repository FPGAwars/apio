# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2

"""Apio scons plugin for the xilinx architecture."""

# pylint: disable=duplicate-code

from pathlib import Path
from SCons.Script import Builder
from SCons.Builder import BuilderBase, CompositeBuilder
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


class PluginXilinx(PluginBase):
    """Apio scons plugin for the Xilinx architecture."""

    def __init__(self, apio_env: ApioEnv):
        # -- Call parent constructor.
        super().__init__(apio_env)

        # -- Cache values.
        yosys_path = Path(apio_env.params.environment.yosys_path)
        self.yosys_lib_dir = yosys_path / "xilinx"
        self.sim_lib_files = [yosys_path / "xilinx" / "cells_sim.v"]
        # -- For lint, also pass the black-box declarations of the primitives
        # -- that have no simulation model in cells_sim.v (PLLE2_*, MMCME2_*,
        # -- etc.); without them verilator fails with MODMISSING on any design
        # -- that instantiates one. The two files declare disjoint modules.
        self.lint_lib_files = self.sim_lib_files + [
            yosys_path / "xilinx" / "cells_xtra.v"
        ]

    def plugin_info(self) -> ArchPluginInfo:
        """Return plugin specific parameters."""
        return ArchPluginInfo(
            constrains_file_suffix=".xdc",
            pnr_file_suffix=".frames",
            bitstream_file_suffix=".bit",
        )

    # @overrides
    def make_synth_builder(self) -> BuilderBase | CompositeBuilder:
        """Creates and returns the synth builder."""

        # -- Keep short references.
        apio_env = self.apio_env
        params = apio_env.params
        xilinx_params = params.fpga_info.xilinx_params

        # -- The yosys synth builder.
        return Builder(
            action=(
                # -- yosys-extra-options goes INSIDE the synth_xilinx command
                # -- (like the other architectures do with synth_ice40/ecp5/
                # -- gowin), so synth flags such as -nodsp work; it used to
                # -- land after write_json, where it did nothing useful.
                'yosys -p "synth_xilinx -arch {0} -top {1} {2}; '
                'write_json $TARGET " '
                "{3} -DSYNTHESIZE {4} $SOURCES"
            ).format(
                xilinx_params.yosys_arch,
                params.apio_env_params.top_module,
                " ".join(params.apio_env_params.yosys_extra_options),
                "" if params.verbosity.all or params.verbosity.synth else "-q",
                get_define_flags(apio_env),
            ),
            suffix=".json",
            source_scanner=self.verilog_src_scanner,
            src_suffix=SRC_SUFFIXES,
        )

    # @overrides
    def make_pnr_builder(self) -> BuilderBase | CompositeBuilder:
        """Creates and returns the pnr builder."""

        # -- Keep short references.
        apio_env = self.apio_env
        params = apio_env.params
        xilinx_params = params.fpga_info.xilinx_params

        # -- We use an emmiter to add to the builder a second output file.
        def emitter(target, source, env):
            _ = env  # Unused
            target.append(apio_env.target + ".pnr")
            return target, source

        # -- Create the builder
        return Builder(
            action=(
                "nextpnr-xilinx --chipdb {0} --xdc {1} --json $SOURCE "
                "--fasm $TARGET --report {2} {3} {4}"
            ).format(
                xilinx_params.chipdb_file_path,
                self.constrain_file(),
                apio_env.target + ".pnr",
                ("" if params.verbosity.all or params.verbosity.pnr else "-q"),
                " ".join(params.apio_env_params.nextpnr_extra_options),
            ),
            src_suffix=".json",
            suffix=".fasm",
            emitter=emitter,
        )

    # @overrides
    def make_bitstream_builder(self) -> BuilderBase | CompositeBuilder:
        """Creates and returns the bitstream builder."""

        # -- Keep short references.
        apio_env = self.apio_env
        params = apio_env.params
        xilinx_params = params.fpga_info.xilinx_params

        prjxray_db = Path(apio_env.params.environment.xilinx_prjxray_db_path)
        prjxray_db = prjxray_db / xilinx_params.yosys_family
        part_file = prjxray_db / xilinx_params.yosys_part / "part.yaml"

        # -- Intermediate .frames file path expression. When resolved, it's
        # -- the same as target file but with the ".frames" extension.
        frames_file_macro = "${TARGET.base}.frames"

        return Builder(
            action=[
                # -- STEP1: Converts .fasm to .frames
                "fasm2frames --part {0} --db-root {1} "
                " $SOURCE > {2} ".format(
                    xilinx_params.yosys_part, prjxray_db, frames_file_macro
                ),
                # -- STEP2 Converts .frames to .bit
                "xc7frames2bit --part_file {0} --part_name {1} "
                "--frm_file {2} --output_file $TARGET".format(
                    part_file, xilinx_params.yosys_part, frames_file_macro
                ),
            ],
            src_suffix=".fasm",
            suffix=".bit",
        )

    # @overrides
    def make_testbench_compile_builder(self) -> BuilderBase | CompositeBuilder:
        """Creates and returns the testbench compile builder."""

        # -- Keep short references.
        apio_env = self.apio_env
        params = apio_env.params

        # -- Sanity checks
        assert apio_env.targeting_one_of("sim", "test")
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
                    is_interactive=apio_env.targeting_one_of("sim"),
                    lib_dirs=[self.yosys_lib_dir],
                    lib_files=self.sim_lib_files,
                ),
            ]
            return action

        # -- The testbench compiler builder.
        return Builder(
            # -- Dynamic action string generator.
            generator=action_generator,
            source_scanner=self.verilog_src_scanner,
            src_suffix=SRC_SUFFIXES,
            suffix=".out",
        )

    # @overrides
    def make_lint_config_builder(self) -> BuilderBase:
        """Creates and returns the lint config builder."""

        # -- Sanity checks
        assert self.apio_env.targeting_one_of("lint")

        # -- Make the builder.
        # -- See https://verilator.org/guide/latest/warnings.html
        return make_verilator_config_builder(
            self.yosys_lib_dir,
            rules_to_suppress=[
                "SPECIFYIGN",
            ],
        )

    # @overrides
    def make_lint_builder(self) -> BuilderBase | CompositeBuilder:
        """Creates and returns the lint builder."""

        return Builder(
            action=verilator_lint_action(
                self.apio_env,
                lib_dirs=[self.yosys_lib_dir],
                lib_files=self.lint_lib_files,
            ),
            source_scanner=self.verilog_src_scanner,
            src_suffix=SRC_SUFFIXES,
        )
