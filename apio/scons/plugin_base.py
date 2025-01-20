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
from click import secho
from SCons.Builder import BuilderBase
from SCons.Action import Action
from SCons.Script import Builder
from apio.scons.apio_env import ApioEnv, TARGET, BUILD_DIR_SEP
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
        return Builder(
            action="vvp $SOURCE -dumpfile=$TARGET",
            suffix=".vcd",
            src_suffix=".out",
        )

    def yosys_dot_builder(self) -> BuilderBase:
        """Creates and returns the yosys dot builder."""
        apio_env = self.apio_env
        params = apio_env.params
        graph_params = params.cmds.graph

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
        """Creates and returns the graphviz renderer builder."""
        apio_env = self.apio_env
        params = apio_env.params
        graph_params = params.cmds.graph

        # --Decode the graphic spec. Currently it's trivial since it
        # -- contains a single value.
        if graph_params.graph_spec:
            # -- This is the case when scons target is 'graph'.
            graph_type = graph_params.graph_spec
            assert graph_type in SUPPORTED_GRAPH_TYPES, graph_type
        else:
            # -- This is the case when scons target is not 'graph'.
            graph_type = "svg"

        def completion_action(source, target, env):  # noqa
            """Action function that prints a completion message."""
            _ = (source, target, env)  # Unused
            secho(
                f"Generated {TARGET}.{graph_type}",
                fg="green",
                bold=True,
                color=True,
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
