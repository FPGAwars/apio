# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""A class with common services for the apio scons handlers.
"""

# C0209: Formatting could be an f-string (consider-using-f-string)
# pylint: disable=C0209

# W0613: Unused argument
# pylint: disable=W0613

import os
from typing import Dict, List
from click import secho
from SCons.Script.SConscript import SConsEnvironment
from SCons.Environment import BuilderWrapper
import SCons.Defaults
from apio.scons.apio_args import ApioArgs


# -- All the build files and other artifcats are created in this this
# -- subdirectory.
BUILD_DIR = "_build"

# -- A shortcut with '/' or '\' appended to the build dir name.
BUILD_DIR_SEP = BUILD_DIR + os.sep

# -- Target name. This is the base file name for various build artifacts.
TARGET = BUILD_DIR_SEP + "hardware"


# pylint: disable=too-many-public-methods
class ApioEnv:
    """Provides abstracted scons env and other user services."""

    def __init__(
        self,
        # scons_arch: SconsArch,
        scons_args: Dict[str, str],
        command_line_targets: List[str],
        is_debug: bool,
    ):
        # -- Save the arguments.
        # self.scons_arch = scons_arch
        self.command_line_targets = command_line_targets
        self.is_debug = is_debug

        # -- Create the underlying scons env.
        self.env = SConsEnvironment(ENV=os.environ, tools=[])

        self.args = ApioArgs.make(scons_args, is_debug)

        # -- Since we ae not using the default environment, make sure it was
        # -- not used unintentionally, e.v. in tests that run create multiple
        # -- scons env in the same session.
        # --
        # pylint: disable=protected-access
        assert (
            SCons.Defaults._default_env is None
        ), "DefaultEnvironment already exists"
        # pylint: enable=protected-access

        # -- Determine if we run on windows. Platform id is a required arg.
        self.is_windows = "windows" in self.args.PLATFORM_ID.lower()

        # Extra info for debugging.
        if self.is_debug:
            self.dump_env_vars()

    def targeting(self, target_name: str) -> bool:
        """Returns true if the named target was specified in the command
        line."""
        return target_name in self.command_line_targets

    def builder(self, builder_id: str, builder):
        """Append to the scons env a builder with given id. The env
        adds it to the BUILDERS dict and also adds to itself an attribute with
        that name that contains a wrapper to that builder."""
        self.env.Append(BUILDERS={builder_id: builder})

    def builder_target(
        self,
        *,
        builder_id: str,
        target,
        sources: List,
        always_build: bool = False,
    ):
        """Creates an return a target that uses the builder with given id."""
        builder_wrapper: BuilderWrapper = getattr(self.env, builder_id)
        target = builder_wrapper(target, sources)
        if always_build:
            self.env.AlwaysBuild(target)
        return target

    def alias(self, name, *, source, action=None, allways_build: bool = False):
        """Creates a target with given dependencies"""
        target = self.env.Alias(name, source, action)
        if allways_build:
            self.env.AlwaysBuild(target)
        return target

    def depends(self, target, dependency):
        """Adds a dependency of one target on another."""
        self.env.Depends(target, dependency)

    def dump_env_vars(self) -> None:
        """Prints a list of the environment variables. For debugging."""
        dictionary = self.env.Dictionary()
        keys = list(dictionary.keys())
        keys.sort()
        secho()
        secho(">>> Env vars BEGIN", fg="magenta", color=True)
        for key in keys:
            print(f"{key} = {self.env[key]}")
        secho("<<< Env vars END\n", fg="magenta", color=True)
