"""
Tests of subprocess_env.py, in particular the LD_LIBRARY_PATH fix for the
Linux pyinstaller bundle. See https://github.com/FPGAwars/apio/issues/887
"""

from apio.common.apio_platforms import get_apio_platforms
from apio.common.proto.apio_common_pb2 import EnvMutations
from apio.common.subprocess_env import (
    apply_env_mutations,
    get_env_mutations_for_subprocess,
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
