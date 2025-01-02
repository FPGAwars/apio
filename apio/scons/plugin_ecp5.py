# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2

"""Apio scons plugin for the ecp5 architecture."""

# R0801: Similar lines
# pylint: disable=R0801

import os
from SCons.Script import Builder
from SCons.Builder import BuilderBase
from apio.scons.apio_env import ApioEnv, TARGET, BUILD_DIR
from apio.scons.plugin_base import PluginBase, ArchPluginInfo
from apio.scons.plugin_util import (
    verilator_lint_action,
    has_testbench_name,
    source_file_issue_action,
    iverilog_action,
    basename,
    vlt_path,
    make_verilator_config_builder,
)


# pylint: disable=consider-using-f-string
class PluginEcp5(PluginBase):
    """Apio scons plugin for the ice40 architecture."""

    def __init__(self, apio_env: ApioEnv):
        # -- Call parent constructor.
        super().__init__(apio_env)

        # -- Cache values.
        self.database_path = os.path.join(
            apio_env.args.TRELLIS_PATH, "database"
        )
        self.yosys_lib_dir = apio_env.args.YOSYS_PATH + "/ecp5"
        self.constrain_file_extension = ".lpf"

    def plugin_info(self) -> ArchPluginInfo:
        """Return plugin specific parameters."""
        return ArchPluginInfo(
            constrains_file_ext=".lpf",
            clk_name_index=2,
        )

    # @overrides
    def synth_builder(self) -> BuilderBase:
        """Creates and returns the synth builder."""
        # -- Keep short references.
        apio_env = self.apio_env
        args = apio_env.args

        # -- The yosys synth builder.
        return Builder(
            action='yosys -p "synth_ecp5 {0} -json $TARGET" {1} '
            "$SOURCES".format(
                ("-top " + args.TOP_MODULE) if args.TOP_MODULE else "",
                "" if args.VERBOSE_ALL or args.VERBOSE_YOSYS else "-q",
            ),
            suffix=".json",
            src_suffix=".v",
            source_scanner=self.verilog_src_scanner,
        )

    # @overrides
    def pnr_builder(self) -> BuilderBase:
        """Creates and returns the pnr builder."""
        # -- Keep short references.
        apio_env = self.apio_env
        args = apio_env.args

        # -- We use an emmiter to add to the builder a second output file.
        def emitter(target, source, env):
            _ = env  # Unused
            target.append(TARGET + ".pnr")
            return target, source

        # -- Create the builder.
        return Builder(
            action=(
                "nextpnr-ecp5 --{0} --package {1} "
                "--json $SOURCE --textcfg $TARGET "
                "--report {2} --lpf {3} {4} --timing-allow-fail --force"
            ).format(
                # pylint: disable=fixme
                # TODO: Explain why 12k -> 25k.
                # TODO: 12k looks more like size than type. Why?
                "25k" if (args.FPGA_TYPE == "12k") else args.FPGA_TYPE,
                args.FPGA_PACK,
                TARGET + ".pnr",
                self.constrain_file(),
                "" if args.VERBOSE_ALL or args.VERBOSE_PNR else "-q",
            ),
            suffix=".config",
            src_suffix=".json",
            emitter=emitter,
        )

    # @overrides
    def bitstream_builder(self) -> BuilderBase:
        """Creates and returns the bitstream builder."""
        apio_env = self.apio_env
        args = apio_env.args
        return Builder(
            action="ecppack --compress --db {0} {1} $SOURCE "
            "{2}/hardware.bit".format(
                self.database_path,
                "" if not args.FPGA_IDCODE else f"--idcode {args.FPGA_IDCODE}",
                BUILD_DIR,
            ),
            suffix=".bit",
            src_suffix=".config",
        )

    # @overrides
    def testbench_compile_builder(self) -> BuilderBase:
        """Creates and returns the testbench compile builder."""
        # -- Keep short references.
        apio_env = self.apio_env
        args = apio_env.args

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
                    verbose=args.VERBOSE_ALL,
                    vcd_output_name=testbench_name,
                    is_interactive=apio_env.targeting("sim"),
                    lib_dirs=[self.yosys_lib_dir],
                ),
            ]
            return action

        # -- The testbench compiler builder.
        return Builder(
            # -- Dynamic action string generator.
            generator=action_generator,
            suffix=".out",
            src_suffix=".v",
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
                f'lint_off -rule PINMISSING  -file "{yosys_vlt_path}/*"',
                f'lint_off -rule ASSIGNIN    -file "{yosys_vlt_path}/*"',
                f'lint_off -rule WIDTHTRUNC  -file "{yosys_vlt_path}/*"',
                f'lint_off -rule INITIALDLY  -file "{yosys_vlt_path}/*"',
            ]
        )

    # @overrides
    def lint_builder(self) -> BuilderBase:
        """Creates and returns the lint builder."""
        # -- Keep short references.
        apio_env = self.apio_env
        args = apio_env.args

        return Builder(
            action=verilator_lint_action(
                warnings_all=args.VERILATOR_ALL,
                warnings_no_style=args.VERILATOR_NO_STYLE,
                no_warns=args.VERILATOR_NOWARNS,
                warns=args.VERILATOR_WARNS,
                top_module=args.TOP_MODULE,
                lib_dirs=[self.yosys_lib_dir],
            ),
            src_suffix=".v",
            source_scanner=self.verilog_src_scanner,
        )
