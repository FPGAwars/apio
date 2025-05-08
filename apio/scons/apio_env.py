# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""A class with common services for the apio scons handlers."""


import os
from typing import List, Optional
from SCons.Script.SConscript import SConsEnvironment
from SCons.Environment import BuilderWrapper
import SCons.Defaults
from apio.common.apio_console import cout
from apio.common.apio_styles import EMPH3
from apio.common.proto.apio_pb2 import SconsParams


class ApioEnv:
    """Provides abstracted scons env and other user services."""

    def __init__(
        self,
        command_line_targets: List[str],
        scons_params: SconsParams,
    ):
        # -- Save the arguments.
        self.command_line_targets = command_line_targets
        self.params = scons_params

        # -- Create the underlying scons env.
        self.scons_env = SConsEnvironment(ENV=os.environ, tools=[])

        # -- Since we ae not using the default environment, make sure it was
        # -- not used unintentionally, e.v. in tests that run create multiple
        # -- scons env in the same session.
        # --
        assert (
            SCons.Defaults._default_env is None
        ), "DefaultEnvironment already exists"

        # Extra info for debugging.
        if self.is_debug:
            self.dump_env_vars()

    @property
    def is_windows(self):
        """Returns True if we run on windows."""
        return self.params.environment.is_windows

    @property
    def is_debug(self):
        """Returns true if we run in debug mode."""
        return self.params.environment.is_debug

    def targeting(self, *target_names) -> bool:
        """Returns true if the any of the named target was specified in the
        scons command line."""
        for target_name in target_names:
            if target_name in self.command_line_targets:
                return True
        return False

    def builder(self, builder_id: str, builder):
        """Append to the scons env a builder with given id. The env
        adds it to the BUILDERS dict and also adds to itself an attribute with
        that name that contains a wrapper to that builder."""
        self.scons_env.Append(BUILDERS={builder_id: builder})

    def builder_target(
        self,
        *,
        builder_id: str,
        target,
        sources: List,
        extra_dependencies: Optional[List] = None,
        always_build: bool = False,
    ):
        """Creates an return a target that uses the builder with given id."""

        # pylint: disable=too-many-arguments

        # -- Scons wraps the builder with a wrapper. We use it to create the
        # -- new target.
        builder_wrapper: BuilderWrapper = getattr(self.scons_env, builder_id)
        target = builder_wrapper(target, sources)
        # -- Mark as 'always build' if requested.
        if always_build:
            self.scons_env.AlwaysBuild(target)
        # -- Add extra dependencies, if any.
        if extra_dependencies:
            for dependency in extra_dependencies:
                self.scons_env.Depends(target, dependency)
        return target

    def alias(self, name, *, source, action=None, always_build: bool = False):
        """Creates a target with given dependencies"""
        target = self.scons_env.Alias(name, source, action)
        if always_build:
            self.scons_env.AlwaysBuild(target)
        return target

    def dump_env_vars(self) -> None:
        """Prints a list of the environment variables. For debugging."""
        dictionary = self.scons_env.Dictionary()
        keys = list(dictionary.keys())
        keys.sort()
        cout("")
        cout(">>> Env vars BEGIN", style=EMPH3)
        for key in keys:
            cout(f"{key} = {self.scons_env[key]}")
        cout("<<< Env vars END\n", style=EMPH3)
