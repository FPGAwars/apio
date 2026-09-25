"""The apio context."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

import os
from dataclasses import dataclass
from typing import Any
from apio.common.apio_console import cout, cstyle
from apio.common.apio_styles import EMPH2, EMPH3
from apio.utils.apio_platforms import ApioPlatform


@dataclass(frozen=True)
class EnvMutations:
    """Contains mutations to the system env."""

    # -- List of env vars to unset.
    unset_vars: list[str]

    # -- PATH items to add.
    paths: list[str]

    # -- Dict with env vars name/value to set.
    set_vars: dict[str, str]


class ToolsRuntimeEnv:
    """A class to manage the runtime environment of tools from the Apio
    packages such as Yosys, Nextpnr, and GtkWave that apio dispatches as
    subprocesses."""

    def __init__(
        self,
        required_packages: dict[str, Any],
        apio_platform: ApioPlatform,
        is_pyinstaller: bool,
    ) -> None:
        self._required_packages = required_packages
        self._apio_platform = apio_platform
        self._is_pyinstaller = is_pyinstaller
        self._env_was_already_set: bool = False

    def scons_shell_id(self) -> str:
        """
        Returns a simplified string name of the shell that SCons will use
        for executing shell-dependent commands. See code below for possible
        values.
        """

        # pylint: disable=too-many-return-statements

        # -- Handle windows.
        if self._apio_platform.is_windows:
            comspec = os.environ.get("COMSPEC", "").lower()
            if "powershell.exe" in comspec or "pwsh.exe" in comspec:
                return "powershell"
            if "cmd.exe" in comspec:
                return "cmd"
            return "unknown"

        # -- Handle the rest (macOS, Linux, etc.)
        shell_path = os.environ.get("SHELL", "").lower()
        if "bash" in shell_path:
            return "bash"
        if "zsh" in shell_path:
            return "zsh"
        if "fish" in shell_path:
            return "fish"
        if "dash" in shell_path:
            return "dash"
        if "ksh" in shell_path:
            return "ksh"
        if "csh" in shell_path or "tcsh" in shell_path:
            return "cshell"
        return "unknown"

    def _determine_env_mutations(self) -> EnvMutations:
        """Collects the env mutation for each of the defined packages,
        in the order they are defined."""

        unset_vars: list[str] = []
        paths: list[str] = []
        set_vars: dict[str, str] = {}
        for _, package_config in self._required_packages.items():
            # -- Get the json 'env' section. We require it, even if it's empty,
            # -- for clarity reasons.
            assert "env" in package_config
            package_env = package_config["env"]

            # -- Collect the env vars to delete.
            delete_env_vars_section = package_env.get("delete-env-vars", [])
            for var_name in delete_env_vars_section:
                # -- Detect duplicates.
                assert var_name not in unset_vars, var_name
                unset_vars.append(var_name)

            # -- Collect the path values.
            package_paths = package_env.get("add-to-path", [])
            paths.extend(package_paths)

            # -- Collect the env vars to add (name, value) pairs.
            add_env_vars_section = package_env.get("add-env-vars", {})
            for var_name, var_value in add_env_vars_section.items():
                # -- Detect duplicates.
                assert var_name not in set_vars, var_name
                set_vars[var_name] = var_value

        return EnvMutations(unset_vars, paths, set_vars)

    def _dump_env_mutations(self, mutations: EnvMutations) -> None:
        """Dumps a user friendly representation of the env mutations."""
        cout("Environment settings:", style=EMPH2)

        # -- Special case for windows.
        windows = self._apio_platform.is_windows

        # -- Print unset vars.
        for name in mutations.unset_vars:
            styled_name = cstyle(name, style=EMPH3)
            if windows:
                cout(f"  set {styled_name}=")
            else:
                cout(f"  unset {styled_name}")

        # -- Dump paths.
        for p in reversed(mutations.paths):
            styled_name = cstyle("PATH", style=EMPH3)
            if windows:
                cout(f"  set {styled_name}={p};%PATH%")
            else:
                cout(f'  {styled_name}="{p}:$PATH"')

        # -- Print set vars.
        for name, val in mutations.set_vars.items():
            styled_name = cstyle(name, style=EMPH3)
            if windows:
                cout(f"  set {styled_name}={val}")
            else:
                cout(f'  {styled_name}="{val}"')

    def _apply_env_mutations(self, mutations: EnvMutations) -> None:
        """Apply a given set of env mutations, while preserving their order."""

        # -- Apply the unset var mutations
        for name in mutations.unset_vars:
            os.environ.pop(name, None)

        # -- Apply the path mutations, while preserving order.
        # -- NOTE: We treat the old path items as a single items.
        old_val = os.environ["PATH"]
        items = mutations.paths + [old_val]
        new_val = os.pathsep.join(items)
        os.environ["PATH"] = new_val

        # -- Apply the set var mutations
        for name, value in mutations.set_vars.items():
            os.environ[name] = value

    def set_env_for_tools(
        self, *, quiet: bool = False, verbose: bool = False
    ) -> None:
        """Sets the environment variables for using all the that are
        available for this platform, even if currently not installed.

        The function sets the environment only on first call and in latter
        calls skips the operation silently.

        If quite is set, no output is printed. When verbose is set, additional
        output such as the env vars mutations are printed, otherwise, a minimal
        information is printed to make the user aware that they commands they
        see are executed in a modified env settings.
        """

        # -- If this fails, this is a programming error. Quiet and verbose
        # -- cannot be combined.
        assert not (quiet and verbose), "Can't have both quite and verbose."

        # -- Collect the env mutations for all packages.
        mutations = self._determine_env_mutations()

        if verbose:
            self._dump_env_mutations(mutations)

        # -- If this is the first call in this apio invocation, apply the
        # -- mutations. These mutations are temporary for the lifetime of this
        # -- process and does not affect the user's shell environment.
        # -- The mutations are also inherited by child processes such as the
        # -- scons processes.
        if not self._env_was_already_set:
            self._apply_env_mutations(mutations)
            self._env_was_already_set = True
            if not verbose and not quiet:
                cout("Setting shell vars.")
