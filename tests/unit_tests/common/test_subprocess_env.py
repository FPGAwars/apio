"""
Tests of subprocess_env.py, in particular the LD_LIBRARY_PATH fix for the
Linux pyinstaller bundle. See https://github.com/FPGAwars/apio/issues/887
"""

from pathlib import Path
from tests.conftest import ApioRunner
from apio.common.apio_platforms import get_apio_platforms
from apio.common.proto.stubs.apio_common_pb2 import EnvMutations
from apio.common.subprocess_env import (
    apply_env_mutations,
    get_env_mutations_for_subprocess,
)
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)

LINUX = get_apio_platforms()["linux-x86-64"]
DARWIN = get_apio_platforms()["darwin-arm64"]


def test_fix_flag_only_for_pyinstaller_on_linux():
    """The fix is requested only for a pyinstaller app on Linux."""

    mutations = get_env_mutations_for_subprocess(LINUX, True, {})
    assert mutations.pyinstaller_linux_fix

    mutations = get_env_mutations_for_subprocess(LINUX, False, {})
    assert not mutations.pyinstaller_linux_fix

    mutations = get_env_mutations_for_subprocess(DARWIN, True, {})
    assert not mutations.pyinstaller_linux_fix

    mutations = get_env_mutations_for_subprocess(DARWIN, False, {})
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
