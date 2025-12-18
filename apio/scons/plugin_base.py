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

from pathlib import Path
from dataclasses import dataclass
from typing import List
import webbrowser
from SCons.Builder import BuilderBase
from SCons.Action import Action
from SCons.Script import Builder
from SCons.Node.FS import File
from SCons.Script.SConscript import SConsEnvironment
from SCons.Node.Alias import Alias
from apio.common.apio_console import cout
from apio.common.apio_styles import SUCCESS
from apio.common.common_util import SRC_SUFFIXES
from apio.scons.apio_env import ApioEnv
from apio.common.proto.apio_pb2 import GraphOutputType
from apio.scons.plugin_util import (
    verilog_src_scanner,
    get_constraint_file,
    get_define_flags,
)


# -- Supported apio graph types.
SUPPORTED_GRAPH_TYPES = ["svg", "pdf", "png"]


@dataclass(frozen=True)
class ArchPluginInfo:
    """Provides information about the plugin."""

    constrains_file_ext: str
    bin_file_suffix: str
    clk_name_index: int


class PluginBase:
    """Base apio arch plugin handler"""

    def __init__(self, apio_env: ApioEnv):
        self.apio_env = apio_env

        # -- Scanner for verilog source files.
        self.verilog_src_scanner = verilog_src_scanner(apio_env)

        # -- A placeholder for the constraint file name.
        self._constrain_file: str = None

    def plugin_info(self) -> ArchPluginInfo:  # pragma: no cover
        """Return plugin specific parameters."""
        raise NotImplementedError("Implement in subclass.")

    def constrain_file(self) -> str:
        """Finds and returns the constraint file path."""
        # -- Keep short references.
        apio_env = self.apio_env

        # -- On first call, determine and cache.
        if self._constrain_file is None:
            self._constrain_file = get_constraint_file(
                apio_env, self.plugin_info().constrains_file_ext
            )
        return self._constrain_file

    def synth_builder(self) -> BuilderBase:  # pragma: no cover
        """Creates and returns the synth builder."""
        raise NotImplementedError("Implement in subclass.")

    def pnr_builder(self) -> BuilderBase:  # pragma: no cover
        """Creates and returns the pnr builder."""
        raise NotImplementedError("Implement in subclass.")

    def bitstream_builder(self) -> BuilderBase:  # pragma: no cover
        """Creates and returns the bitstream builder."""
        raise NotImplementedError("Implement in subclass.")

    def testbench_compile_builder(self) -> BuilderBase:  # pragma: no cover
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
            else params.apio_env_params.top_module
        )

        return Builder(
            # See https://tinyurl.com/yosys-sv-graph
            # For -wireshape see https://github.com/YosysHQ/yosys/pull/4252
            action=(
                'yosys -p "read_verilog -sv $SOURCES; show -format dot'
                ' -colors 1 -wireshape plaintext -prefix {0} {1}" {2} {3}'
            ).format(
                apio_env.graph_target,
                top_module,
                "" if params.verbosity.all else "-q",
                get_define_flags(apio_env),
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

        def completion_action(
            target: List[Alias],
            source: List[File],
            env: SConsEnvironment,
        ):  # noqa
            """Action function that prints a completion message and if
            requested, open a viewer on the output file.."""
            _ = (source, env)  # Unused
            # -- Get the rendered file.
            target_file: File = target[0]
            assert isinstance(target_file, File)
            # -- Print a message
            cout(f"Generated {str(target_file)}", style=SUCCESS)
            # -- If requested, convert the file to URI and open it in the
            # -- default browser.
            if graph_params.open_viewer:
                cout("Opening default browser")
                file_path = Path(target_file.get_abspath())
                file_uri = file_path.resolve().as_uri()
                default_browser = webbrowser.get()
                default_browser.open(file_uri)
            else:
                cout("User requested no graph viewer")

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

    def lint_config_builder(self) -> BuilderBase:  # pragma: no cover
        """Creates and returns the lint config builder."""
        raise NotImplementedError("Implement in subclass.")

    def lint_builder(self) -> BuilderBase:  # pragma: no cover
        """Creates and returns the lint builder."""
        raise NotImplementedError("Implement in subclass.")
