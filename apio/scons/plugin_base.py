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

from dataclasses import dataclass
import click
from SCons.Builder import BuilderBase
from SCons.Action import Action
from SCons.Script import Builder
from apio.scons.apio_env import ApioEnv, TARGET, BUILD_DIR_SEP


# -- Supported apio graph types.
SUPPORTED_GRAPH_TYPES = ["svg", "pdf", "png"]


def unused(*_):
    """Fake a use of an unused variable or argument."""
    # pass


@dataclass(frozen=True)
class ArchPluginInfo:
    """Provides information about the plugin."""

    constrains_file_ext: str
    clk_name_index: int


# pylint: disable=consider-using-f-string
class PluginBase:
    """Base apio arch plugin handler"""

    def __init__(self, apio_env: ApioEnv):
        self.apio_env = apio_env
        # self.constrain_file_ext = constrain_file_ext

        # -- Place holder for the constrain file. We create it on demand and
        # -- cache its value here.
        self._constrain_file: str = None

    def plugin_info(self) -> ArchPluginInfo:
        """Return plugin specific parameters."""
        raise NotImplementedError("Implement in subclass.")

    def constrain_file(self) -> str:
        """Finds and returns the constrain file path."""
        if self._constrain_file is None:
            # -- This is the first time we are asked for the constrain file.
            self._constrain_file = self.apio_env.get_constraint_file(
                self.plugin_info().constrains_file_ext,
                self.apio_env.args.TOP_MODULE,
            )
        return self._constrain_file

    def synth_builder(self) -> BuilderBase:
        """Creates and returns the synth builder."""
        raise NotImplementedError("Implement in subclass.")

    def pnr_builder(self) -> BuilderBase:
        """Creates and returns the pnr builder."""
        raise NotImplementedError("Implement in subclass.")

    def bitstream_builder(self) -> BuilderBase:
        """Creates and returns the bitstream builder."""
        raise NotImplementedError("Implement in subclass.")

    def testbench_compile_builder(self) -> BuilderBase:
        """Creates and returns the testbench compile builder."""
        raise NotImplementedError("Implement in subclass.")

    def testbench_run_builder(self) -> BuilderBase:
        """Creates and returns the testbench run builder."""
        return Builder(
            action="vvp $SOURCE -dumpfile=$TARGET",
            suffix=".vcd",
            src_suffix=".out",
        )

    def yosys_dot_builder(self) -> BuilderBase:
        """Creates and returns the yosys dot builder."""
        apio_env = self.apio_env
        args = apio_env.args

        return Builder(
            action=(
                'yosys -f verilog -p "show -format dot -colors 1 '
                '-prefix {0}hardware {1}" {2} $SOURCES'
            ).format(
                BUILD_DIR_SEP,
                args.TOP_MODULE if args.TOP_MODULE else "unknown_top",
                "" if args.VERBOSE_ALL else "-q",
            ),
            suffix=".dot",
            src_suffix=".v",
            source_scanner=apio_env.verilog_src_scanner(),
        )

    def graphviz_renderer_builder(self) -> BuilderBase:
        """Creates and returns the graphviz renderer builder."""
        apio_env = self.apio_env
        args = apio_env.args
        # return apio_env.graphviz_builder(args.GRAPH_SPEC)

        # --Decode the graphic spec. Currently it's trivial since it
        # -- contains a single value.
        if args.GRAPH_SPEC:
            # -- This is the case when scons target is 'graph'.
            graph_type = args.GRAPH_SPEC
            assert graph_type in SUPPORTED_GRAPH_TYPES, graph_type
        else:
            # -- This is the case when scons target is not 'graph'.
            graph_type = "svg"

        def completion_action(source, target, env):
            """Action function that prints a completion message."""
            unused(source, target, env)
            click.secho(
                f"Generated {TARGET}.{graph_type}", fg="green", color=True
            )

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

    def lint_config_builder(self) -> BuilderBase:
        """Creates and returns the lint config builder."""
        raise NotImplementedError("Implement in subclass.")

    def lint_builder(self) -> BuilderBase:
        """Creates and returns the lint builder."""
        raise NotImplementedError("Implement in subclass.")
