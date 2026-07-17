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
            clk_name_index=0,
        )

    # @overrides
    def synth_builder(self) -> BuilderBase | CompositeBuilder:
        """Creates and returns the synth builder."""

        # -- Keep short references.
        apio_env = self.apio_env
        params = apio_env.params
        xilinx_params = params.fpga_info.xilinx_params

        # -- The yosys synth builder.
        return Builder(
            action=(
                'yosys -p "synth_xilinx -arch {0} -top {1}; '
                'write_json $TARGET  {2} " '
                "{3} -DSYNTHESIZE {4} $SOURCES"
            ).format(
                xilinx_params.yosys_arch,
                params.apio_env_params.top_module,
                " ".join(params.apio_env_params.yosys_extra_options),
                "" if params.verbosity.all or params.verbosity.synth else "-q",
                get_define_flags(apio_env),
            ),
            suffix=".json",
            src_suffix=SRC_SUFFIXES,
            source_scanner=self.verilog_src_scanner,
        )

    # @overrides
    def pnr_builder(self) -> BuilderBase | CompositeBuilder:
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

        package = xilinx_params.package
        database = f"{package}.bin"
        chipdb = Path(apio_env.params.environment.chipdb_path)

        # -- Python file that is passed to nextpnr-xilinx for generating
        # -- the report file

        # -- Get the full path of this file (plugin_xilinx.py)
        current_python_file = Path(__file__)

        # -- The parent folder is the apio root folder
        apio_root = current_python_file.parent.parent

        # -- Add the report_xilinx.py folder to the path
        report_py = apio_root / "scons/report_xilinx.py"

        # -- Create the builder
        return Builder(
            action=(
                "nextpnr-xilinx --chipdb {0} --xdc {1} --json $SOURCE "
                "--fasm $TARGET "
                "--post-route {2} "
                "-q "
                "{3}"
            ).format(
                chipdb / database,
                self.constrain_file(),
                report_py,
                " ".join(params.apio_env_params.nextpnr_extra_options),
            ),
            suffix=".fasm",
            src_suffix=".json",
            emitter=emitter,
        )

    # @overrides
    def bitstream_pre_builder(self) -> BuilderBase | CompositeBuilder:
        """Creates and returns the pre-bitstream builder."""

        # -- Keep short references.
        apio_env = self.apio_env
        params = apio_env.params
        xilinx_params = params.fpga_info.xilinx_params

        part1 = f"{xilinx_params.package}-{xilinx_params.speed}"
        prjxray_db = Path(apio_env.params.environment.prjxray_db_path)
        prjxray_db = prjxray_db / xilinx_params.family

        return Builder(
            action="fasm2frames --part {0} --db-root {1} "
            " $SOURCE > $TARGET ".format(
                part1,
                prjxray_db,
            ),
            suffix=".frames",
            src_suffix=".fasm",
        )

    # @overrides
    def bitstream_builder(self) -> BuilderBase | CompositeBuilder:
        """Creates and returns the bitstream builder."""

        # -- Keep short references.
        apio_env = self.apio_env
        params = apio_env.params
        xilinx_params = params.fpga_info.xilinx_params
        part1 = f"{xilinx_params.package}-{xilinx_params.speed}"

        prjxray_db = Path(apio_env.params.environment.prjxray_db_path)
        prjxray_db = prjxray_db / xilinx_params.family
        part_file = prjxray_db / part1 / "part.yaml"

        return Builder(
            action="xc7frames2bit --part_file {0} --part_name {1} "
            "--frm_file "
            "$SOURCE --output_file $TARGET".format(
                part_file,
                part1,
            ),
            suffix=".bit",
            src_suffix=".frames",
        )

    # @overrides
    def testbench_compile_builder(self) -> BuilderBase | CompositeBuilder:
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
            suffix=".out",
            src_suffix=SRC_SUFFIXES,
            source_scanner=self.verilog_src_scanner,
        )

    # @overrides
    def lint_config_builder(self) -> BuilderBase:
        """Creates and returns the lint config builder."""

        # -- Sanity checks
        assert self.apio_env.targeting_one_of("lint")

        # -- Make the builder.
        return make_verilator_config_builder(
            self.yosys_lib_dir,
            rules_to_supress=[
                "SPECIFYIGN",
            ],
        )

    # @overrides
    def lint_builder(self) -> BuilderBase | CompositeBuilder:
        """Creates and returns the lint builder."""

        return Builder(
            action=verilator_lint_action(
                self.apio_env,
                lib_dirs=[self.yosys_lib_dir],
                lib_files=self.lint_lib_files,
            ),
            src_suffix=SRC_SUFFIXES,
            source_scanner=self.verilog_src_scanner,
        )
