"""
Tests of apio_profile.py
"""

import json
from test.conftest import ApioRunner
from apio.profile import Profile

TEST_DATA = {
    "installed-packages": {
        "examples": {"version": "0.1.4"},
        "verible": {"version": "0.0.1"},
    },
    "preferences": {"theme": "light"},
    "remote-config": {
        "packages": {
            "drivers": {"version": "1.2.0"},
            "examples": {"version": "0.1.4"},
        }
    },
}


def test_profile_loading(apio_runner: ApioRunner):
    """Tests the loading and validation of a profile file."""

    with apio_runner.in_sandbox() as sb:

        # -- Write a test profile.json file.
        path = sb.home_dir / "profile.json"
        sb.write_file(path, json.dumps(TEST_DATA, indent=2))

        # -- Read back the content.
        profile = Profile(sb.home_dir, "http://fake-domain.com/config")

        # -- Verify
        assert profile.preferences == TEST_DATA["preferences"]
        assert profile.packages == TEST_DATA["installed-packages"]
        assert profile.remote_config == TEST_DATA["remote-config"]
        assert not profile.remote_config_fetched
