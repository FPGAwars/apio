# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""A class with common services for the apio scons handlers.
"""

# C0209: Formatting could be an f-string (consider-using-f-string)
# pylint: disable=C0209

# W0613: Unused argument
# pylint: disable=W0613

import os
from pathlib import Path
from typing import List, Optional
from SCons.Script.SConscript import SConsEnvironment
from SCons.Environment import BuilderWrapper
import SCons.Defaults
from apio.common.apio_console import cout

# from apio.scons.apio_args import ApioArgs
from apio.common.proto.apio_pb2 import SconsParams


# -- The build directory. This is a relative path from the project directory.
BUILD_DIR = Path("_build")

# -- Target name. This is the base file name for various build artifacts.
TARGET = str(BUILD_DIR / "hardware")


# pylint: disable=too-many-public-methods
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
        # pylint: disable=protected-access
        assert (
            SCons.Defaults._default_env is None
        ), "DefaultEnvironment already exists"
        # pylint: enable=protected-access

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

    # pylint: disable=too-many-arguments
    def builder_target(
        self,
        *,
        builder_id: str,
        target,
        sources: List,
        extra_dependecies: Optional[List] = None,
        always_build: bool = False,
    ):
        """Creates an return a target that uses the builder with given id."""
        # -- Scons wraps the builder with a wrapper. We use it to create the
        # -- new target.
        builder_wrapper: BuilderWrapper = getattr(self.scons_env, builder_id)
        target = builder_wrapper(target, sources)
        # -- Mark as 'always build' if requested.
        if always_build:
            self.scons_env.AlwaysBuild(target)
        # -- Add extra dependencies, if any.
        if extra_dependecies:
            for dependency in extra_dependecies:
                self.scons_env.Depends(target, dependency)
        return target

    def alias(self, name, *, source, action=None, allways_build: bool = False):
        """Creates a target with given dependencies"""
        target = self.scons_env.Alias(name, source, action)
        if allways_build:
            self.scons_env.AlwaysBuild(target)
        return target

    def dump_env_vars(self) -> None:
        """Prints a list of the environment variables. For debugging."""
        dictionary = self.scons_env.Dictionary()
        keys = list(dictionary.keys())
        keys.sort()
        cout("")
        cout(">>> Env vars BEGIN", style="magenta")
        for key in keys:
            cout(f"{key} = {self.scons_env[key]}")
        cout("<<< Env vars END\n", style="magenta")
