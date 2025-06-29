"""
Tests of apio_profile.py
"""

import json
import copy
from test.conftest import ApioRunner
from apio.profile import Profile
from apio.utils import util


TEST_DATA = {
    "installed-packages": {
        "drivers": {"version": "2025.06.13"},
        "examples": {"version": "2025.06.21"},
    },
    "preferences": {"theme": "light"},
    "remote-config": {
        "metadata": {
            "loaded-at": "2025-06-29-07-18",
            "loaded-by": util.get_apio_version(),
            "loaded-from": (
                "https://github.com/FPGAwars/apio/raw/develop/"
                "remote-config/apio-0.9.7.jsonc"
            ),
        },
        "packages": {
            "drivers": {
                "release": {
                    "package-file": "apio-drivers-${PLATFORM}-${YYYYMMDD}.tgz",
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

        # -- Write a test profile.json file.
        path = sb.home_dir / "profile.json"
        test_data = copy.deepcopy(TEST_DATA)
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
        assert profile.packages == test_data["installed-packages"]
        assert profile.remote_config == test_data["remote-config"]
        assert not profile.remote_config_fetched


def test_profile_loading_config_stale(apio_runner: ApioRunner):
    """Tests the loading and validation of a profile file."""

    with apio_runner.in_sandbox() as sb:

        # -- Write a test profile.json file. We set an old apio version
        # -- to cause the cached remote config to be classified as stale.
        path = sb.home_dir / "profile.json"
        test_data = copy.deepcopy(TEST_DATA)
        test_data["remote-config"]["metadata"]["loaded-by"] = "0.9.6"
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
        assert profile.packages == test_data["installed-packages"]
        assert profile.remote_config == {}  # Config rejected
        assert not profile.remote_config_fetched
