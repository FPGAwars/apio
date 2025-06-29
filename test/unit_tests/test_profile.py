"""
Tests of apio_profile.py
"""

import json
from test.conftest import ApioRunner
from apio.profile import Profile, get_datetime_stamp, datetime_stamp_diff_days
from apio.utils import util
from apio.apio_context import ApioContext, ApioContextScope


def get_test_data(loaded_by_apio_version: str, packages_platform_id: str):
    """Returns a fake profile.json content."""
    return {
        "installed-packages": {
            "drivers": {
                "version": "2025.06.13",
                "platform-id": packages_platform_id,
                "loaded-by": "0.9.7",
                "loaded-at": "2025-06-29-14-48",
                "loaded-from": (
                    "https://github.com/FPGAwars/apio-examples/"
                    "releases/download/2025-06-21/apio-examples-20250621.tgz"
                ),
            },
            "examples": {
                "version": "2025.06.21",
                "platform-id": packages_platform_id,
                "loaded-by": "0.9.7",
                "loaded-at": "2025-06-29-14-48",
                "loaded-from": (
                    "https://github.com/FPGAwars/apio-examples/"
                    "releases/download/2025-06-21/apio-examples-20250621.tgz"
                ),
            },
        },
        "preferences": {"theme": "light"},
        "remote-config": {
            "metadata": {
                "loaded-at": "2025-06-29-07-18",
                "loaded-by": loaded_by_apio_version,
                "loaded-from": (
                    "https://github.com/FPGAwars/apio/raw/develop/"
                    "remote-config/apio-0.9.7.jsonc"
                ),
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
                        "organization": "FPGAwars",
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
                        "organization": "FPGAwars",
                    },
                },
            },
        },
    }


def test_profile_loading_config_ok(apio_runner: ApioRunner):
    """Tests the loading and validation of a profile file."""

    with apio_runner.in_sandbox() as sb:

        apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

        # -- Write a test profile.json file.
        path = sb.home_dir / "profile.json"
        test_data = get_test_data(
            util.get_apio_version(), apio_ctx.platform_id
        )
        sb.write_file(
            path,
            json.dumps(
                test_data,
                indent=2,
            ),
        )

        # -- Read back the content.
        profile = Profile(sb.home_dir, "http://fake-domain.com/config")

        # -- Verify
        assert profile.preferences == test_data["preferences"]
        assert profile.installed_packages == test_data["installed-packages"]
        assert profile.remote_config == test_data["remote-config"]
        assert not profile.remote_config_fetched


def test_profile_loading_config_stale(apio_runner: ApioRunner):
    """Tests the loading and validation of a profile file."""

    with apio_runner.in_sandbox() as sb:

        apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

        # -- Write a test profile.json file. We set an old apio version
        # -- to cause the cached remote config to be classified as stale.
        path = sb.home_dir / "profile.json"
        test_data = get_test_data("0.9.6", apio_ctx.platform_id)
        sb.write_file(
            path,
            json.dumps(
                test_data,
                indent=2,
            ),
        )

        # -- Read back the content.
        profile = Profile(sb.home_dir, "http://fake-domain.com/config")

        # -- Verify
        assert profile.preferences == test_data["preferences"]
        assert profile.installed_packages == test_data["installed-packages"]
        assert profile.remote_config == {}  # Config rejected
        assert not profile.remote_config_fetched


def test_datetime_stamp_diff_days():
    """Test the datetime timestamp diff."""

    ts_now = get_datetime_stamp()
    assert datetime_stamp_diff_days(ts_now, ts_now) == 0

    assert (
        datetime_stamp_diff_days("2025-06-15-07-30", "2025-06-16-00-01") == 1
    )

    assert (
        datetime_stamp_diff_days("2025-06-16-00-01", "2025-06-15-07-30") == -1
    )

    assert (
        datetime_stamp_diff_days("2025-06-15-00-00", "2025-06-15-23-59") == 0
    )

    assert (
        datetime_stamp_diff_days("2025-06-15-00-0x", "2025-06-15-23-59")
        == None
    )

    assert (
        datetime_stamp_diff_days("2025-06-15-20-15", "2025-06-20-00-01") == 5
    )
