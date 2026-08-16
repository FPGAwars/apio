"""
Tests of remote_config.py and it's integration with ApioContext.
"""

# TODO: Add test coverage of the "refresh-failure-on" logic.

import json
from datetime import datetime, timedelta
from pytest import LogCaptureFixture
from tests.conftest import ApioRunner
from apio.managers.remote_config import (
    get_datetime_stamp,
    days_between_datetime_stamps,
)
from apio.utils import util
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)


def get_test_data(
    loaded_by_apio_version: str,
    loaded_at_days: int,
    loaded_from: str,
):
    """Returns a fake cached-remote-config.json content. 'loaded_at_days' is
    the value of the remote config "loaded-at" relative to today in days."""
    loaded_at_datetime = datetime.now() + timedelta(days=loaded_at_days)
    loaded_at_stamp = get_datetime_stamp(loaded_at_datetime)
    assert isinstance(loaded_at_stamp, str)

    return {
        "remote-config": {
            "packages": {
                "drivers": {
                    "repository": {
                        "organization": "fpgawars",
                        "name": "tools-drivers",
                    },
                    "release": {
                        "tag": "2026-08-07",
                        "package": "apio-drivers-${PLATFORM}-${YYYYMMDD}.tgz",
                    },
                },
                "examples": {
                    "repository": {
                        "organization": "fpgawars",
                        "name": "apio-examples",
                    },
                    "release": {
                        "tag": "2026-08-06",
                        "package": "apio-examples-${YYYYMMDD}.tgz",
                    },
                },
            },
        },
        "metadata": {
            "loaded-by": loaded_by_apio_version,
            "loaded-at": loaded_at_stamp,
            "loaded-from": loaded_from,
        },
    }


def test_datetime_stamp_diff_days():
    """Test the datetime timestamp diff."""

    assert (
        get_datetime_stamp(
            datetime(year=2025, month=6, day=30, hour=14, minute=45)
        )
        == "2025-06-30-14-45"
    )

    ts_now = get_datetime_stamp()
    assert (
        days_between_datetime_stamps(
            ts_now,
            ts_now,
            default=9999,
        )
        == 0
    )

    assert (
        days_between_datetime_stamps(
            "2025-06-15-07-30",
            "2025-06-16-00-01",
            default=9999,
        )
        == 1
    )

    assert (
        days_between_datetime_stamps(
            "2025-06-16-00-01",
            "2025-06-15-07-30",
            default=9999,
        )
        == -1
    )

    assert (
        days_between_datetime_stamps(
            "2025-06-15-00-00",
            "2025-06-15-23-59",
            default=9999,
        )
        == 0
    )

    assert (
        days_between_datetime_stamps(
            "2025-06-15-00-0x",
            "2025-06-15-23-59",
            default=9999,
        )
        == 9999
    )

    assert (
        days_between_datetime_stamps(
            "2025-06-15-20-15",
            "2025-06-20-00-01",
            default=9999,
        )
        == 5
    )


def test_cached_config_ok(apio_runner: ApioRunner, capsys: LogCaptureFixture):
    """Tests remote config resolution when the cached config is ok."""

    with apio_runner.in_sandbox() as sb:

        # -- Get an actual fresh remote config.
        capsys.readouterr()  # Reset log.
        base_apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.GET_FRESH,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        assert "Fetching" in capsys.readouterr().out
        remote_config_url = base_apio_ctx.remote_config.metadata["loaded-from"]

        # -- Write a test cached remote config.
        path = sb.home_dir / "cached-remote-config.json"
        test_data = get_test_data(
            util.get_apio_version_str(), 0, remote_config_url
        )
        sb.write_file(
            path,
            json.dumps(
                test_data,
                indent=2,
            ),
            exists_ok=True,
        )

        # -- Init an apio context that should return the test cached
        # -- remote config.
        capsys.readouterr()  # Reset log.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        log = capsys.readouterr().out
        assert "Cached remote config unsuitable" not in log
        assert "Fetching" not in log
        assert apio_ctx.remote_config.data == test_data["remote-config"]


def test_cached_config_different_apio_version(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests remote config resolution when the cached config is from a
    different apio version."""

    with apio_runner.in_sandbox() as sb:

        # -- Get an actual fresh remote config.
        capsys.readouterr()  # Reset log.
        base_apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.GET_FRESH,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        assert "Fetching" in capsys.readouterr().out
        remote_config_url = base_apio_ctx.remote_config.metadata["loaded-from"]

        # -- Write a test cached remote config. Using a fake apio version.
        path = sb.home_dir / "cached-remote-config.json"
        test_data = get_test_data("1.0.0", 0, remote_config_url)
        sb.write_file(
            path,
            json.dumps(
                test_data,
                indent=2,
            ),
            exists_ok=True,
        )

        # -- Init an apio context that should return the test cached
        # -- remote config.
        capsys.readouterr()  # Reset log.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )

        log = capsys.readouterr().out
        assert "Cached remote config unsuitable (Apio version mismatch)" in log
        assert "Fetching" in log
        assert apio_ctx.remote_config.data == base_apio_ctx.remote_config.data


def test_cached_config_different_apio_src_url(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests remote config resolution when the cached config is from a
    different URL."""

    with apio_runner.in_sandbox() as sb:

        # -- Get an actual fresh remote config.
        capsys.readouterr()  # Reset log.
        base_apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.GET_FRESH,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        assert "Fetching" in capsys.readouterr().out

        # -- Write a test cached remote config. Using a fake loaded-from url.
        path = sb.home_dir / "cached-remote-config.json"
        test_data = get_test_data(
            util.get_apio_version_str(), 0, "https://github.com/fake/url.json"
        )
        sb.write_file(
            path,
            json.dumps(
                test_data,
                indent=2,
            ),
            exists_ok=True,
        )

        # -- Init an apio context that should return the test cached
        # -- remote config.
        capsys.readouterr()  # Reset log.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )

        log = capsys.readouterr().out
        assert "Cached remote config unsuitable (source URL mismatch)" in log
        assert "Fetching" in log
        assert apio_ctx.remote_config.data == base_apio_ctx.remote_config.data


def test_cached_remote_config_too_old(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests remote config resolution when the cached config is too old."""

    with apio_runner.in_sandbox() as sb:

        # -- Get an actual fresh remote config.
        capsys.readouterr()  # Reset log.
        base_apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.GET_FRESH,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        assert "Fetching" in capsys.readouterr().out
        remote_config_url = base_apio_ctx.remote_config.metadata["loaded-from"]

        # -- Write a test cached remote config that is 10 days old.
        path = sb.home_dir / "cached-remote-config.json"
        test_data = get_test_data(
            util.get_apio_version_str(), -10, remote_config_url
        )
        sb.write_file(
            path,
            json.dumps(
                test_data,
                indent=2,
            ),
            exists_ok=True,
        )

        # -- Init an apio context that should return a fresh remote config.
        capsys.readouterr()  # Reset log.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        log = capsys.readouterr().out
        assert "Cached remote config unsuitable (stale)" in log
        assert "Fetching" in log
        assert apio_ctx.remote_config.data == base_apio_ctx.remote_config.data


def test_cached_remote_config_too_new(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests remote config resolution when the cached config is
    from the future."""

    with apio_runner.in_sandbox() as sb:

        # -- Get an actual fresh remote config.
        capsys.readouterr()  # Reset log.
        base_apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.GET_FRESH,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        assert "Fetching" in capsys.readouterr().out
        remote_config_url = base_apio_ctx.remote_config.metadata["loaded-from"]

        # -- Write a test cached remote config that was downloaded 10 days
        # -- in the future.
        path = sb.home_dir / "cached-remote-config.json"
        test_data = get_test_data(
            util.get_apio_version_str(), 10, remote_config_url
        )
        sb.write_file(
            path,
            json.dumps(
                test_data,
                indent=2,
            ),
            exists_ok=True,
        )

        # -- Init an apio context that should return a fresh remote config.
        capsys.readouterr()  # Reset log.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        log = capsys.readouterr().out
        assert "Cached remote config unsuitable (stale)" in log
        assert "Fetching" in log
        assert apio_ctx.remote_config.data == base_apio_ctx.remote_config.data


def test_corrupt_cached_remote_config(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests remote config resolution when the cached config file is
    corrupt."""

    with apio_runner.in_sandbox() as sb:

        # -- Get an actual fresh remote config.
        capsys.readouterr()  # Reset log.
        base_apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.GET_FRESH,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        assert "Fetching" in capsys.readouterr().out

        # -- Write a test cached remote config that is corrupt.
        path = sb.home_dir / "cached-remote-config.json"
        test_data = "{ corrupt json file }"
        sb.write_file(
            path,
            json.dumps(
                test_data,
                indent=2,
            ),
            exists_ok=True,
        )

        # -- Init an apio context that should return a fresh remote config.
        capsys.readouterr()  # Reset log.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        log = capsys.readouterr().out
        assert "Cached remote config unsuitable (could'nt parse)" in log
        assert "Fetching" in log
        assert apio_ctx.remote_config.data == base_apio_ctx.remote_config.data


def test_no_cached_remote_config(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests remote config resolution when there is no cached remote
    config file."""

    with apio_runner.in_sandbox() as sb:

        # -- Check that the cache file doesn't exist.
        path = sb.home_dir / "cached-remote-config.json"
        assert not path.exists()

        # -- Init an apio context that should return a fresh remote config.
        capsys.readouterr()  # Reset log.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        log = capsys.readouterr().out
        assert "Cached remote config unsuitable (no cache file)" in log
        assert "Fetching" in log
        assert "oss-cad-suite" in apio_ctx.remote_config.data["packages"]


def test_forced_fresh_remote_config_ok(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests remote config resolution when the cached config is ignored
    because a fresh config was requested."""

    with apio_runner.in_sandbox() as sb:

        # -- Get an actual fresh remote config.
        capsys.readouterr()  # Reset log.
        base_apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.GET_FRESH,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        assert "Fetching" in capsys.readouterr().out
        remote_config_url = base_apio_ctx.remote_config.metadata["loaded-from"]

        # -- Write a test cached remote config.
        path = sb.home_dir / "cached-remote-config.json"
        test_data = get_test_data(
            util.get_apio_version_str(), 0, remote_config_url
        )
        sb.write_file(
            path,
            json.dumps(
                test_data,
                indent=2,
            ),
            exists_ok=True,
        )

        # -- Init an apio context that should fetch a fresh config.
        capsys.readouterr()  # Reset log.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.GET_FRESH,
            packages_policy=PackagesPolicy.IGNORE_PACKAGES,
        )
        log = capsys.readouterr().out
        assert "Cached remote config unsuitable" not in log
        assert "Fetching" in log
        assert apio_ctx.remote_config.data == base_apio_ctx.remote_config.data
