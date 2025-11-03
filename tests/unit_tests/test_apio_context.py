"""
Tests of apio_context.py
"""

import os
from pathlib import Path
from pytest import LogCaptureFixture, raises
from tests.conftest import ApioRunner
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.common.common_util import PROJECT_BUILD_PATH


def test_init(apio_runner: ApioRunner):
    """Tests the initialization of the apio context."""

    with apio_runner.in_sandbox() as sb:

        # -- Create an apio.ini file.
        sb.write_default_apio_ini()

        # -- Default init.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.PROJECT_REQUIRED,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        assert apio_ctx.has_project

        # -- Verify context's project dir.
        assert str(apio_ctx.project_dir) == "."
        assert apio_ctx.project_dir.samefile(Path.cwd())
        assert apio_ctx.project_dir.samefile(sb.proj_dir)

        # -- Verify context's home and packages dirs.
        assert apio_ctx.apio_home_dir == sb.home_dir
        assert apio_ctx.apio_packages_dir == sb.packages_dir

        # -- Verify build dir
        assert PROJECT_BUILD_PATH == Path("_build")
        assert apio_ctx.env_build_path == Path("_build/default")


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
                ApioContext(
                    project_policy=ProjectPolicy.NO_PROJECT,
                    remote_config_policy=RemoteConfigPolicy.CACHED_OK,
                    packages_policy=PackagesPolicy.ENSURE_PACKAGES,
                )
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
            ApioContext(
                project_policy=ProjectPolicy.NO_PROJECT,
                remote_config_policy=RemoteConfigPolicy.CACHED_OK,
                packages_policy=PackagesPolicy.ENSURE_PACKAGES,
            )
        assert e.value.code == 1
        assert (
            "Error: Apio home dir should be an absolute path"
            in capsys.readouterr().out
        )
