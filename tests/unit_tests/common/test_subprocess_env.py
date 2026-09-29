"""
Tests of subprocess_env.py, in particular the LD_LIBRARY_PATH fix for the
Linux pyinstaller bundle. See https://github.com/FPGAwars/apio/issues/887
"""

from apio.common.apio_platforms import ApioPlatform
from apio.common.proto.apio_common_pb2 import EnvMutations
from apio.common import subprocess_env

LINUX = ApioPlatform(
    id="linux-x86-64", type="Linux", variant="X86 64 bit", is_linux=True
)
DARWIN = ApioPlatform(
    id="darwin-arm64", type="Mac OSX", variant="ARM", is_darwin=True
)

# -- The value that the pyinstaller bootloader exports for the bundled libs.
BUNDLE_LIBS = "/home/me/.apio/bin/_internal"


def _mutations(fix: bool) -> EnvMutations:
    """Returns an env mutations that has only the pyinstaller fix flag."""
    return EnvMutations(pyinstaller_linux_fix=fix)


def test_fix_flag_only_for_pyinstaller_on_linux():
    """The fix is requested only for a pyinstaller app on Linux."""

    def flag(platform: ApioPlatform, is_pyinstaller: bool) -> bool:
        mutations = subprocess_env.get_env_mutations_for_subprocess(
            platform, is_pyinstaller, {}
        )
        return mutations.pyinstaller_linux_fix

    assert flag(LINUX, True)
    assert not flag(LINUX, False)
    assert not flag(DARWIN, True)
    assert not flag(DARWIN, False)


def test_fix_unsets_ld_library_path_when_it_was_not_set_originally():
    """No LD_LIBRARY_PATH_ORIG means that the user had no LD_LIBRARY_PATH and
    the one in the env is the bundle's. The subprocess must not see it,
    otherwise the system's 'sh' loads the bundled libreadline."""

    env = {"PATH": "/usr/bin", "LD_LIBRARY_PATH": BUNDLE_LIBS}
    subprocess_env.apply_env_mutations(_mutations(True), env)

    assert "LD_LIBRARY_PATH" not in env
    assert "LD_LIBRARY_PATH_ORIG" not in env
    assert env["PATH"] == "/usr/bin"


def test_fix_restores_the_original_ld_library_path():
    """A user's LD_LIBRARY_PATH, saved by pyinstaller in LD_LIBRARY_PATH_ORIG,
    is restored and the helper var is hidden from the subprocess."""

    env = {
        "PATH": "/usr/bin",
        "LD_LIBRARY_PATH": BUNDLE_LIBS + ":/opt/user/lib",
        "LD_LIBRARY_PATH_ORIG": "/opt/user/lib",
    }
    subprocess_env.apply_env_mutations(_mutations(True), env)

    assert env["LD_LIBRARY_PATH"] == "/opt/user/lib"
    assert "LD_LIBRARY_PATH_ORIG" not in env


def test_no_fix_leaves_ld_library_path_alone():
    """When the fix is not requested (python package, macOS, windows) the
    LD_LIBRARY_PATH of the user is passed through untouched."""

    env = {"PATH": "/usr/bin", "LD_LIBRARY_PATH": "/opt/user/lib"}
    subprocess_env.apply_env_mutations(_mutations(False), env)

    assert env["LD_LIBRARY_PATH"] == "/opt/user/lib"
    assert "LD_LIBRARY_PATH_ORIG" not in env
