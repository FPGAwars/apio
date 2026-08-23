"""
Tests of profile.py
"""

import json
from pytest import raises
from tests.conftest import ApioRunner
from apio.managers.profile import (
    Profile,
)

TEST_DATA = {
    "preferences": {"theme": "light"},
}


def test_profile_loading(apio_runner: ApioRunner):
    """Tests the loading and validation of a profile file."""

    with apio_runner.in_sandbox() as sb:

        # -- Write a test profile.json file.
        path = sb.home_dir / "profile.json"
        # test_data = get_test_data(apio_ctx, util.get_apio_version_str(), 0)
        sb.write_file(
            path,
            json.dumps(
                TEST_DATA,
                indent=2,
            ),
            exists_ok=True,
        )

        # -- Read back the content.
        profile = Profile(sb.home_dir)

        # -- Verify
        assert profile.preferences == TEST_DATA["preferences"]


def test_profile_with_corrupt_profile_file(apio_runner: ApioRunner):
    """Tests that a corrupt profile.json results in a clean error message
    instead of an unhandled JSONDecodeError on every command."""

    bad_contents = [
        "{ corrupt json",  # -- Not a valid json.
        "[1, 2, 3]",  # -- Not a json dict.
        '{"preferences": "corrupt"}',  # -- Field is not a dict.
    ]

    with apio_runner.in_sandbox() as sb:

        for bad_content in bad_contents:

            # -- Write a corrupt profile.json file.
            sb.write_file(
                sb.home_dir / "profile.json", bad_content, exists_ok=True
            )

            # -- The theme reader should quietly fall back to the default.
            assert Profile.read_preferences_theme(default="dark") == "dark"

            # -- Loading the profile should exit with a clean error message.
            with apio_runner.with_logger() as log:
                with raises(SystemExit) as e:
                    Profile(sb.home_dir)
            assert e.value.code == 1, bad_content
            assert "Invalid profile file" in log.out


def test_profile_with_unknown_theme(apio_runner: ApioRunner):
    """Tests that an unknown theme name in profile.json falls back to the
    default theme instead of crashing every command with an
    AssertionError."""

    with apio_runner.in_sandbox() as sb:
        for bogus_theme in ["no-such-theme", ["dark"], 5, None]:

            # -- Write a profile.json file with a bogus theme value.
            sb.write_file(
                sb.home_dir / "profile.json",
                json.dumps({"preferences": {"theme": bogus_theme}}),
                exists_ok=True,
            )

            # -- The theme reader should quietly fall back to the default.
            assert Profile.read_preferences_theme(default="light") == "light"
