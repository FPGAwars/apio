"""Utilities related to the runtime environment of tools and other
subprocesses."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

import os
from typing import Any
from collections.abc import MutableMapping
from apio.common.debug_util import is_debug
from apio.common.apio_console import cout, cstyle
from apio.common.apio_styles import EMPH2, EMPH3
from apio.common.apio_platforms import ApioPlatform
from apio.common import proto_util
from apio.common.proto.apio_common_pb2 import EnvMutations, NameValue

# -- Env vars involved in pyinstaller fixing under linux.
# -- See See https://github.com/FPGAwars/apio/issues/887
LD_LIBRARY_PATH = "LD_LIBRARY_PATH"
LD_LIBRARY_PATH_ORIG = "LD_LIBRARY_PATH_ORIG"


def scons_shell_id(apio_platform: ApioPlatform) -> str:
    """
    Returns a simplified string name of the shell that SCons will use
    for executing shell-dependent commands. See code below for possible
    values.
    """

    # pylint: disable=too-many-return-statements

    # -- Handle windows.
    if apio_platform.is_windows:
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


def get_env_mutations_for_scons(
    apio_platform: ApioPlatform,
    is_pyinstaller_app: bool,
) -> EnvMutations:
    """Construct an EnvMutations object with the mutations necessary to
    run scons."""

    # -- Determine if we need to fix the env for pyinstaller linux.
    pyinstaller_linux_fix: bool = is_pyinstaller_app and apio_platform.is_linux

    # -- Construct the result.
    result = EnvMutations(
        unset_vars=[],
        add_to_path=[],
        set_vars=[],
        pyinstaller_linux_fix=pyinstaller_linux_fix,
    )

    proto_util.check_is_initialized(
        result, "Failed to initialized EnvMutations"
    )

    # -- All done.
    return result


def get_env_mutations_for_tools(
    required_packages: dict[str, Any],
    apio_platform: ApioPlatform,
    is_pyinstaller_app: bool,
) -> EnvMutations:
    """Return an EnvMutations with the system env mutations for running
    underlying tools such as yosys."""

    # pylint: disable=too-many-locals

    unset_vars: list[str] = []
    paths: list[str] = []
    # set_vars: dict[str, str] = {}
    set_vars: list[NameValue] = []
    for _, package_config in required_packages.items():
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
            for sv in set_vars:
                assert var_name != sv.name, var_name
            # -- Append.
            set_vars.append(NameValue(name=var_name, value=var_value))

    # -- Determine if we need to fix the env for pyinstaller linux.
    pyinstaller_linux_fix: bool = is_pyinstaller_app and apio_platform.is_linux

    # -- Construct the result.
    result = EnvMutations(
        unset_vars=unset_vars,
        add_to_path=paths,
        set_vars=set_vars,
        pyinstaller_linux_fix=pyinstaller_linux_fix,
    )
    proto_util.check_is_initialized(
        result, "Failed to initialized EnvMutations"
    )

    # -- All done.
    return result


def show_env_mutations(
    mutations: EnvMutations, apio_platform: ApioPlatform
) -> None:
    """Dumps a user friendly representation of the env mutations."""
    cout("Environment settings:", style=EMPH2)

    # -- Special case for windows.
    windows = apio_platform.is_windows

    # -- Print unset vars.
    for name in mutations.unset_vars:
        styled_name = cstyle(name, style=EMPH3)
        if windows:
            cout(f"  set {styled_name}=")
        else:
            cout(f"  unset {styled_name}")

    # -- Dump paths.
    for p in reversed(mutations.add_to_path):
        styled_name = cstyle("PATH", style=EMPH3)
        if windows:
            cout(f"  set {styled_name}={p};%PATH%")
        else:
            cout(f'  {styled_name}="{p}:$PATH"')

    # -- Print set vars.
    for sv in mutations.set_vars:
        styled_name = cstyle(sv.name, style=EMPH3)
        if windows:
            cout(f"  set {styled_name}={sv.value}")
        else:
            cout(f'  {styled_name}="{sv.value}"')

    # -- NOTE For now we don't dump the pyinstaller fix mutation since
    # -- it's internal to Apio (not user facing)


def apply_env_mutations(
    mutations: EnvMutations, env: MutableMapping[str, str]
) -> None:
    """Apply a given set of env mutations, while preserving their order."""

    # -- Apply the unset var mutations
    for name in mutations.unset_vars:
        env.pop(name, None)

    # -- Apply the path mutations, while preserving order.
    # -- NOTE: We treat the old path items as a single items.
    old_val = env["PATH"]
    items = list(mutations.add_to_path) + [old_val]
    new_val = os.pathsep.join(items)
    env["PATH"] = new_val

    # -- Apply the set var mutations
    for sv in mutations.set_vars:
        env[sv.name] = sv.value

    # -- For now we fix only for linux
    proto_util.check_is_required(mutations, "pyinstaller_linux_fix")
    if not mutations.pyinstaller_linux_fix:
        return

    if is_debug(1):
        cout(f"Fixing {LD_LIBRARY_PATH} for linux pyinstaller.")

    # -- Get the initial values of the vars
    pre_ld_library_path: str | None = env.get(LD_LIBRARY_PATH)
    pre_ld_library_path_orig: str | None = env.get(LD_LIBRARY_PATH_ORIG)

    if is_debug(1):
        cout(f"[pre-fix] {LD_LIBRARY_PATH}={pre_ld_library_path}")
        cout(f"[pre-fix] {LD_LIBRARY_PATH_ORIG}={pre_ld_library_path_orig}")

    # -- Fix LD_LIBRARY_PATH and LD_LIBRARY_PATH_ORIG
    if pre_ld_library_path_orig is None:
        # -- LD_LIBRARY_PATH was originally unset but pyinstaller set it
        # -- up. Unset it.
        env.pop(LD_LIBRARY_PATH, None)
    else:
        # -- LD_LIBRARY_PATH was originally set, restore the original
        # -- value.
        env[LD_LIBRARY_PATH] = pre_ld_library_path_orig
        # -- Unset LD_LIBRARY_PATH_ORIG. Since we will ignore future
        # -- requests for fixing, we don't need it anymore and we want to
        # -- hide it from the tool, to preserve the original env.
        env.pop(LD_LIBRARY_PATH_ORIG, None)

    # -- Show outcome.
    if is_debug(1):
        post_ld_library_path = env.get(LD_LIBRARY_PATH)
        post_ld_library_path_orig = env.get(LD_LIBRARY_PATH_ORIG)
        cout(f"[post-fix] {LD_LIBRARY_PATH}={post_ld_library_path}")
        cout(
            f"[post-fix] {LD_LIBRARY_PATH_ORIG}="
            + f"{post_ld_library_path_orig}"
        )
