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
from SCons.Builder import BuilderBase
from SCons.Action import Action
from SCons.Script import Builder
from apio.scons.apio_env import ApioEnv, TARGET, BUILD_DIR_SEP
from apio.proto.apio_pb2 import GraphOutputType
from apio.scons.scons_console import cprint
from apio.scons.plugin_util import (
    SRC_SUFFIXES,
    verilog_src_scanner,
    get_constraint_file,
)


# -- Supported apio graph types.
SUPPORTED_GRAPH_TYPES = ["svg", "pdf", "png"]


@dataclass(frozen=True)
class ArchPluginInfo:
    """Provides information about the plugin."""

    constrains_file_ext: str
    bin_file_suffix: str
    clk_name_index: int


# pylint: disable=consider-using-f-string
class PluginBase:
    """Base apio arch plugin handler"""

    def __init__(self, apio_env: ApioEnv):
        self.apio_env = apio_env

        # -- Scanner for verilog source files.
        self.verilog_src_scanner = verilog_src_scanner(apio_env)

        # -- A laceholder for the constrain file name.
        self._constrain_file: str = None

    def plugin_info(self) -> ArchPluginInfo:
        """Return plugin specific parameters."""
        raise NotImplementedError("Implement in subclass.")

    def constrain_file(self) -> str:
        """Finds and returns the constrain file path."""
        # -- Keep short references.
        apio_env = self.apio_env
        params = apio_env.params

        # -- On first call, determine and cache.
        if self._constrain_file is None:
            self._constrain_file = get_constraint_file(
                apio_env,
                self.plugin_info().constrains_file_ext,
                params.project.top_module,
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

        # -- Sanity checks
        assert self.apio_env.targeting("sim", "test")
        assert self.apio_env.params.target.HasField(
            "sim"
        ) or self.apio_env.params.target.HasField("test")

        return Builder(
            action="vvp $SOURCE -dumpfile=$TARGET",
            suffix=".vcd",
            src_suffix=".out",
        )

    def yosys_dot_builder(self) -> BuilderBase:
        """Creates and returns the yosys dot builder. Should be called
        only when serving the graph command."""

        # -- Sanity checks
        assert self.apio_env.targeting("graph")
        assert self.apio_env.params.target.HasField("graph")

        # -- Shortcuts.
        apio_env = self.apio_env
        params = apio_env.params
        graph_params = params.target.graph

        # -- Determine top module value. First priority is to the
        # -- graph cmd param.
        top_module = (
            graph_params.top_module
            if graph_params.top_module
            else params.project.top_module
        )

        return Builder(
            action=(
                'yosys -f verilog -p "show -format dot -colors 1 '
                '-prefix {0}hardware {1}" {2} $SOURCES'
            ).format(
                BUILD_DIR_SEP,
                top_module,
                "" if params.verbosity.all else "-q",
            ),
            suffix=".dot",
            src_suffix=SRC_SUFFIXES,
            source_scanner=self.verilog_src_scanner,
        )

    def graphviz_renderer_builder(self) -> BuilderBase:
        """Creates and returns the graphviz renderer builder. Should
        be called only when serving the graph command."""

        # -- Sanity checks.
        assert self.apio_env.targeting("graph")
        assert self.apio_env.params.target.HasField("graph")

        # -- Shortcuts.
        apio_env = self.apio_env
        params = apio_env.params
        graph_params = params.target.graph

        # -- Determine the output type string.
        type_map = {
            GraphOutputType.PDF: "pdf",
            GraphOutputType.PNG: "png",
            GraphOutputType.SVG: "svg",
        }
        type_str = type_map[graph_params.output_type]
        assert type_str, f"Unexpected graph type {graph_params.output_type}"

        def completion_action(source, target, env):  # noqa
            """Action function that prints a completion message."""
            _ = (source, target, env)  # Unused
            cprint(f"Generated {TARGET}.{type_str}", style="green")

        actions = [
            f"dot -T{type_str} $SOURCES -o $TARGET",
            Action(completion_action, "completion_action"),
        ]

        graphviz_builder = Builder(
            # Expecting graphviz dot to be installed and in the path.
            action=actions,
            suffix=f".{type_str}",
            src_suffix=".dot",
        )

        return graphviz_builder

    def lint_config_builder(self) -> BuilderBase:
        """Creates and returns the lint config builder."""
        raise NotImplementedError("Implement in subclass.")

    def lint_builder(self) -> BuilderBase:
        """Creates and returns the lint builder."""
        raise NotImplementedError("Implement in subclass.")
