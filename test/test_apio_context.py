"""
Tests of apio_context.py
"""

import os
from pathlib import Path
from test.conftest import ApioRunner
from pytest import LogCaptureFixture, raises
from apio.apio_context import ApioContext, ApioContextScope


def test_init(apio_runner: ApioRunner):
    """Tests the initialization of the apio context."""

    with apio_runner.in_sandbox() as sb:

        # -- Create an apio.ini file.
        sb.write_default_apio_ini()

        # -- Default init.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        assert apio_ctx.has_project

        # -- Verify context's project dir.
        assert str(apio_ctx.project_dir) == "."
        assert apio_ctx.project_dir.samefile(Path.cwd())
        assert apio_ctx.project_dir.samefile(sb.proj_dir)

        # -- Verify context's home and packages dirs.
        assert apio_ctx.home_dir == sb.home_dir
        assert apio_ctx.packages_dir == sb.packages_dir

        # -- Verify build dirs
        assert apio_ctx.build_all_path == Path("_build")
        assert apio_ctx.build_env_path == Path("_build/default")


def test_home_dir_with_a_bad_character(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests the initialization of the apio context with home dirs that
    contain invalid chars."""

    for invalid_char in ["ó", "ñ", " ", "😼"]:
        with apio_runner.in_sandbox() as sb:

            # -- Make up a home dir path with the invalid char.
            invalid_home_dir = sb.sandbox_dir / f"apio-{invalid_char}-home"
            os.environ["APIO_HOME"] = str(invalid_home_dir)

            # -- Initialize an apio context. It should exit with an error.
            with raises(SystemExit) as e:
                ApioContext(scope=ApioContextScope.NO_PROJECT)
            assert e.value.code == 1
            assert (
                f"Unsupported character [{invalid_char}]"
                in capsys.readouterr().out
            )


def test_home_dir_with_relative_path(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Apio context should fail if the apio home dir is a relative path"""

    with apio_runner.in_sandbox():

        # -- Make up a home dir path with the invalid char.
        invalid_home_dir = Path("./aa/bb")
        os.environ["APIO_HOME"] = str(invalid_home_dir)

        # -- Initialize an apio context. It should exit with an error.
        with raises(SystemExit) as e:
            ApioContext(scope=ApioContextScope.NO_PROJECT)
        assert e.value.code == 1
        assert (
            "Error: Apio home dir should be an absolute path"
            in capsys.readouterr().out
        )


def test_snap_user_common(apio_runner: ApioRunner):
    """Test that SNAP_USER_COMMON sets home dir."""
    # -- Test with SNAP_USER_COMMON and no APIO_HOME. Home should come
    # -- from SNAP_USER_COMMON
    with apio_runner.in_sandbox() as sb:
        # -- Delete the APIO_HOME definition that was set by the sandbox.
        os.environ.pop("APIO_HOME")
        # -- Simulate a snap env definition.
        snap_home = str((sb.home_dir / "aaa/bbb").absolute())
        os.environ["SNAP_USER_COMMON"] = snap_home
        # -- Create an apio context.
        apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)
        # -- Verify that the home path came from SNAP_USER_COMMON.
        assert str(apio_ctx.home_dir) == snap_home

    # -- Test with both APIO_HOME and SNAP_USER_COMMON. APIO_HOME should
    # -- have a higher priority.
    with apio_runner.in_sandbox() as sb:
        # -- Make sure the sandbox set APIO_HOME
        assert os.environ["APIO_HOME"] == str(sb.home_dir)
        # -- Simulate a snap env definition.
        snap_home = str((sb.home_dir / "aaa/bbb").absolute())
        os.environ["SNAP_USER_COMMON"] = snap_home
        # -- Create an apio context.
        apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)
        # -- Verify that the home path came from APIO_HOME.
        assert str(apio_ctx.home_dir) == str(sb.home_dir)
