"""
Tests of apio_profile.py
"""

import json
from datetime import datetime, timedelta
from tests.conftest import ApioRunner
from apio.profile import (
    Profile,
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
    apio_ctx: ApioContext,
    loaded_by_apio_version: str,
    loaded_at_days: int,
):
    """Returns a fake profile.json content. 'loaded_at_days' is the value of
    the remote config "loaded-at" relative to today in days."""
    loaded_at_datetime = datetime.now() + timedelta(days=loaded_at_days)
    loaded_at_stamp = get_datetime_stamp(loaded_at_datetime)
    assert isinstance(loaded_at_stamp, str)

    return {
        "preferences": {"theme": "light"},
        "remote-config": {
            "metadata": {
                "loaded-at": loaded_at_stamp,
                "loaded-by": loaded_by_apio_version,
                "loaded-from": apio_ctx.profile.remote_config_url,
            },
            "packages": {
                "drivers": {
                    "release": {
                        "package-file": (
                            "apio-drivers-${PLATFORM}-${YYYYMMDD}.tgz"
                        ),
                        "release-tag": "${YYYY-MM-DD}",
                        "version": "2025.06.13",
                    },
                    "repository": {
                        "name": "tools-drivers",
                        "organization": "fpgawars",
                    },
                },
                "examples": {
                    "release": {
                        "package-file": "apio-examples-${YYYYMMDD}.tgz",
                        "release-tag": "${YYYY-MM-DD}",
                        "version": "2025.06.21",
                    },
                    "repository": {
                        "name": "apio-examples",
                        "organization": "fpgawars",
                    },
                },
            },
        },
    }


def test_profile_loading_config_ok(apio_runner: ApioRunner):
    """Tests the loading and validation of a profile file with no need
    to fetch a remote config."""

    with apio_runner.in_sandbox() as sb:

        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        # -- Write a test profile.json file.
        path = sb.home_dir / "profile.json"
        test_data = get_test_data(apio_ctx, util.get_apio_version_str(), 0)
        sb.write_file(
            path,
            json.dumps(
                test_data,
                indent=2,
            ),
            exists_ok=True,
        )

        # -- Read back the content.
        profile = Profile(
            sb.home_dir,
            sb.packages_dir,
            apio_ctx.profile.remote_config_url,
            5,  # TTL in days
            60,  # Remote config retry mins.
            RemoteConfigPolicy.CACHED_OK,
        )

        # -- Verify
        assert profile.preferences == test_data["preferences"]
        assert profile.remote_config == test_data["remote-config"]


def test_profile_loading_config_stale_version(apio_runner: ApioRunner):
    """Tests the loading and validation of a profile file that include
    an old config that needs to be refreshed."""

    with apio_runner.in_sandbox() as sb:

        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        # -- Write a test profile.json file. We set an old apio version
        # -- to cause the cached remote config to be classified as stale.
        path = sb.home_dir / "profile.json"
        original_loaded_by = "0.9.6"
        assert original_loaded_by != util.get_apio_version_str()
        test_data = get_test_data(apio_ctx, original_loaded_by, 0)

        sb.write_file(
            path,
            json.dumps(
                test_data,
                indent=2,
            ),
            exists_ok=True,
        )

        # -- Read back the content.
        profile = Profile(
            sb.home_dir,
            sb.packages_dir,
            apio_ctx.profile.remote_config_url,
            5,  # TTL in days
            60,  # Remote config retry mins.
            RemoteConfigPolicy.CACHED_OK,
        )

        # -- Verify. Remote config should be a fresh one, loaded by this
        # -- apio version.
        assert profile.preferences == test_data["preferences"]
        # assert profile.installed_packages == test_data["installed-packages"]
        assert (
            profile.remote_config["metadata"]["loaded-by"]
            == util.get_apio_version_str()
        )


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
