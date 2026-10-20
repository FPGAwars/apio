# This file is part of the Apio project
# (C) 2016-present FPGAwars
# Project authors:
#   * Jesús Arroyo (Jesus89) (2016-2019)
#   * Juan Gonzalez (obijuan) (2019-2024)
#   * The Apio Team (2024-present)
# License: GPLv2

"""
Tests of subprocess_env.py, in particular the LD_LIBRARY_PATH fix for the
Linux pyinstaller bundle. See https://github.com/FPGAwars/apio/issues/887
"""

import os
from pathlib import Path
import pytest
from tests.conftest import ApioRunner
from apio.common.apio_console import cunstyle
from apio.common.apio_platforms import get_apio_platforms
from apio.common.proto.stubs.apio_common_pb2 import EnvMutations, NameValue
from apio.common.subprocess_env import (
    apply_env_mutations,
    get_env_mutations_for_subprocess,
    show_env_mutations,
)
from apio.common.proto.stubs.apio_config_pb2 import ApioPlatformEnvSpec
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)

# -- ApioPlatform instances.
LINUX = get_apio_platforms()["linux-x86-64"]
DARWIN = get_apio_platforms()["darwin-arm64"]
WINDOWS = get_apio_platforms()["windows-amd64"]


def test_fix_flag_only_for_pyinstaller_on_linux():
    """The fix is requested only for a pyinstaller app on Linux."""

    empty_env_spec = ApioPlatformEnvSpec()

    mutations = get_env_mutations_for_subprocess(LINUX, True, empty_env_spec)
    assert mutations.pyinstaller_linux_fix

    mutations = get_env_mutations_for_subprocess(LINUX, False, empty_env_spec)
    assert not mutations.pyinstaller_linux_fix

    mutations = get_env_mutations_for_subprocess(DARWIN, True, empty_env_spec)
    assert not mutations.pyinstaller_linux_fix

    mutations = get_env_mutations_for_subprocess(DARWIN, False, empty_env_spec)
    assert not mutations.pyinstaller_linux_fix


def test_fix_unsets_ld_library_path_when_it_was_not_set_originally():
    """No LD_LIBRARY_PATH_ORIG means that the user had no LD_LIBRARY_PATH and
    the one in the env is the bundle's. The subprocess must not see it,
    otherwise the system's 'sh' loads the bundled libreadline."""

    env = {
        "PATH": "/usr/bin",
        "LD_LIBRARY_PATH": "/home/me/.apio/bin/_internal",
    }
    apply_env_mutations(EnvMutations(pyinstaller_linux_fix=True), env)
    assert env == {"PATH": "/usr/bin"}


def test_fix_restores_the_original_ld_library_path():
    """A user's LD_LIBRARY_PATH, saved by pyinstaller in LD_LIBRARY_PATH_ORIG,
    is restored and the helper var is hidden from the subprocess."""

    env = {
        "PATH": "/usr/bin",
        "LD_LIBRARY_PATH": "/home/me/.apio/bin/_internal:/opt/user/lib",
        "LD_LIBRARY_PATH_ORIG": "/opt/user/lib",
    }
    apply_env_mutations(EnvMutations(pyinstaller_linux_fix=True), env)
    assert env == {"PATH": "/usr/bin", "LD_LIBRARY_PATH": "/opt/user/lib"}


def test_no_fix_leaves_ld_library_path_alone():
    """When the fix is not requested (python package, macOS, windows) the
    LD_LIBRARY_PATH of the user is passed through untouched."""

    env = {"PATH": "/usr/bin", "LD_LIBRARY_PATH": "/opt/user/lib"}
    apply_env_mutations(EnvMutations(pyinstaller_linux_fix=False), env)
    assert env == {"PATH": "/usr/bin", "LD_LIBRARY_PATH": "/opt/user/lib"}


def test_path_mutation_with_unset_or_empty_path(apio_runner: ApioRunner):
    """An unset or empty PATH is a fatal error."""

    # -- The sandbox configures the apio console.
    with apio_runner.in_sandbox():
        mutations = EnvMutations(add_to_path=["/a/bin", "/b/bin"])

        env: dict[str, str]
        for env in [{}, {"PATH": ""}]:
            with apio_runner.with_logger() as log:
                with pytest.raises(SystemExit) as e:
                    apply_env_mutations(mutations, env)
            assert e.value.code == 1, env
            assert "The PATH env var is not set or is empty" in log.out, env


def test_path_mutation_prepends_to_path():
    """The added path items are prepended, in order, to the old PATH."""

    mutations = EnvMutations(add_to_path=["/a/bin", "/b/bin"])
    env = {"PATH": "/usr/bin"}
    apply_env_mutations(mutations, env)
    assert env == {"PATH": os.pathsep.join(["/a/bin", "/b/bin", "/usr/bin"])}


def test_path_conflicts(apio_runner: ApioRunner):
    """Test that there are no conflicting items along the Apio PATH
    mutations."""

    with apio_runner.in_sandbox() as sb:

        # -- Create an ApioContext with access to Apio packages.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        # -- Get the path mutations in order of search (first is highest
        # -- priority)
        mutations: EnvMutations = apio_ctx.get_env_mutations_for_subprocess(
            include_apio_packages=True
        )
        apio_path_dirs = mutations.add_to_path

        # -- Collect items on path
        print(f"{apio_path_dirs=}")
        matches: dict[str, list[Path]] = {}
        for dir in apio_path_dirs:
            dir_path = Path(dir)
            files_paths: list[Path] = [
                p for p in dir_path.glob("*") if p.is_file()
            ]
            for file_path in files_paths:
                matches.setdefault(file_path.name, []).append(file_path)

        # -- Report
        for name, files in matches.items():
            if len(files) > 1:
                data = files[0].read_bytes()
                same = all(p.read_bytes() == data for p in files[1:])
                print(f"\n{name} {same}")
                for file in files:
                    print(f"- {str(file)}")


def test_show_env_mutations(apio_runner: ApioRunner):
    """Tests that the env mutations are shown as valid shell commands,
    with added vars exported on non windows platforms so user can
    copy/paste them."""

    # -- The sandbox configures the apio console.
    with apio_runner.in_sandbox():

        mutations = EnvMutations(
            add_to_path=["/my/bin"],
            delete_env_var=["PYTHONPATH"],
            add_env_vars=[NameValue(name="MY_VAR", value="my-value")],
        )

        # -- Non windows.
        with apio_runner.with_logger() as log:
            show_env_mutations(mutations, LINUX)
        out = cunstyle(log.out)
        assert 'PATH="/my/bin:$PATH"' in out
        assert 'export PATH="' not in out
        assert "unset PYTHONPATH" in out
        assert 'export MY_VAR="my-value"' in out

        # -- Windows.
        with apio_runner.with_logger() as log:
            show_env_mutations(mutations, WINDOWS)
        out = cunstyle(log.out)
        assert "set PATH=/my/bin;%PATH%" in out
        assert "set PYTHONPATH=" in out
        assert "set MY_VAR=my-value" in out
        assert "export" not in out
