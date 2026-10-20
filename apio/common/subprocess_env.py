# This file is part of the Apio project
# (C) 2016-present FPGAwars
# Project authors:
#   * Jesús Arroyo (Jesus89) (2016-2019)
#   * Juan Gonzalez (obijuan) (2019-2024)
#   * The Apio Team (2024-present)
# License: GPLv2

"""Utilities related to the runtime environment of tools and other
subprocesses."""

import os
from collections.abc import MutableMapping
from apio.common.debug_util import is_debug
from apio.common.apio_console import cout, cstyle, fatal_error
from apio.common.apio_styles import EMPH2, EMPH3
from apio.common.apio_platforms import ApioPlatform
from apio.common import proto_util
from apio.common.proto.stubs.apio_common_pb2 import EnvMutations, NameValue
from apio.common.proto.stubs.apio_config_pb2 import ApioPlatformEnvSpec

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


def get_env_mutations_for_subprocess(
    apio_platform: ApioPlatform,
    is_pyinstaller_app: bool,
    env_spec: ApioPlatformEnvSpec | None,
) -> EnvMutations:
    """Return an EnvMutations with the system env mutations for running a
    subprocess. If apio_packages is not empty, the mutations includes also
    mutation to use the included apio packages (e.g. 'yosys' from
    oss-cad-suite)."""

    assert env_spec is None or isinstance(env_spec, ApioPlatformEnvSpec), type(
        env_spec
    )

    delete_env_var: list[str] = []
    paths: list[str] = []
    add_env_vars: list[NameValue] = []

    if env_spec is not None:
        # -- Collect the env vars to delete.
        for var_name in env_spec.delete_env_vars:
            # -- Detect duplicates.
            assert var_name not in delete_env_var, var_name
            delete_env_var.append(var_name)

        # -- Collect the path values to add.
        paths.extend(env_spec.add_to_path)

        # -- Collect the env vars to add (name, value) pairs.
        for name, value in env_spec.add_env_vars.items():
            # -- Detect duplicates.
            for add_var in add_env_vars:
                assert name != add_var.name, name
            # -- Append.
            add_env_vars.append(NameValue(name=name, value=value))

    # -- Determine if we need to fix the env for pyinstaller linux.
    pyinstaller_linux_fix: bool = is_pyinstaller_app and apio_platform.is_linux

    # -- Construct the result.
    result = EnvMutations(
        add_to_path=paths,
        delete_env_var=delete_env_var,
        add_env_vars=add_env_vars,
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

    # -- Print paths.
    for p in reversed(mutations.add_to_path):
        styled_name = cstyle("PATH", style=EMPH3)
        if windows:
            cout(f"  set {styled_name}={p};%PATH%")
        else:
            cout(f'  {styled_name}="{p}:$PATH"')

    # -- Print delete vars.
    for name in mutations.delete_env_var:
        styled_name = cstyle(name, style=EMPH3)
        if windows:
            cout(f"  set {styled_name}=")
        else:
            cout(f"  unset {styled_name}")

    # -- Print add vars.
    for sv in mutations.add_env_vars:
        styled_name = cstyle(sv.name, style=EMPH3)
        if windows:
            cout(f"  set {styled_name}={sv.value}")
        else:
            # -- Export so the var is visible to processes started by the
            # -- shell, e.g. if the user copy/pastes these lines.
            cout(f'  export {styled_name}="{sv.value}"')

    # -- NOTE For now we don't dump the pyinstaller fix mutation since
    # -- it's internal to Apio (not user facing)


def apply_env_mutations(
    mutations: EnvMutations, env: MutableMapping[str, str]
) -> None:
    """Apply a given set of env mutations, while preserving their order."""

    # -- Apply the path mutations, while preserving order.
    # -- NOTE: We treat the old path items as a single items.
    old_val = env.get("PATH")
    if not old_val:
        fatal_error("The PATH env var is not set or is empty.")
    items = list(mutations.add_to_path) + [old_val]
    env["PATH"] = os.pathsep.join(items)

    # -- Apply the unset var mutations
    for name in mutations.delete_env_var:
        env.pop(name, None)

    # -- Apply the set var mutations
    for sv in mutations.add_env_vars:
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
