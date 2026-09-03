"""Test for the "apio drivers" command."""

import pytest
from tests.conftest import ApioRunner
from apio.utils import apio_platforms
from apio.commands.apio import apio_top_cli as apio

# TODO: add a test for ubuntu
# TODO: add a (dummy) test for windows


def test_drivers_darwin_only(apio_runner: ApioRunner):
    """Tests the 'apio drivers' commands on darwin platform."""
    # -- Skip this test if not running on a darwin platform
    if not apio_platforms.get_apio_platform().is_darwin:
        pytest.skip("Darwin only test")

    with apio_runner.in_sandbox() as sb:

        # -- Run 'apio drivers install ftdi'
        result = sb.invoke_apio_cmd(apio, ["drivers", "install", "ftdi"])
        sb.assert_result_ok(result)
        assert (
            "No driver installation is required on this platform"
            in result.output
        )

        # -- Run 'apio drivers uninstall ftdi'
        result = sb.invoke_apio_cmd(apio, ["drivers", "uninstall", "ftdi"])
        sb.assert_result_ok(result)
        assert (
            "No driver installation is required on this platform"
            in result.output
        )

        # -- Run 'apio drivers install serial'
        result = sb.invoke_apio_cmd(apio, ["drivers", "install", "serial"])
        sb.assert_result_ok(result)
        assert (
            "No driver installation is required on this platform"
            in result.output
        )

        # -- Run 'apio drivers uninstall serial'
        result = sb.invoke_apio_cmd(apio, ["drivers", "uninstall", "serial"])
        sb.assert_result_ok(result)
        assert (
            "No driver installation is required on this platform"
            in result.output
        )


def test_drivers_github_linux_only(apio_runner: ApioRunner):
    """Tests the 'apio drivers' commands on linux platform."""

    # -- Skip this test if not running on a linux platform
    if not apio_platforms.get_apio_platform().is_linux:
        pytest.skip("Ubuntu only test")

    # -- Skip this test if not running on a github workflow. We need
    # -- the github password-less sudo for this test to succeed.
    if not apio_runner.is_on_github_workflow():
        pytest.skip("Github workflow only test")

    with apio_runner.in_sandbox() as sb:

        # -- Run 'apio drivers install ftdi'
        result = sb.invoke_apio_cmd(apio, ["drivers", "install", "ftdi"])
        sb.assert_result_ok(result)
        print(result.output)
        assert "FTDI drivers installed" in result.output

        # -- Run 'apio drivers uninstall ftdi'
        result = sb.invoke_apio_cmd(apio, ["drivers", "uninstall", "ftdi"])
        sb.assert_result_ok(result)
        print(result.output)
        assert "FTDI drivers uninstalled" in result.output

        # -- Run 'apio drivers install serial'
        result = sb.invoke_apio_cmd(apio, ["drivers", "install", "serial"])
        sb.assert_result_ok(result)
        assert "Serial drivers installed" in result.output

        # -- Run 'apio drivers uninstall serial'
        result = sb.invoke_apio_cmd(apio, ["drivers", "uninstall", "serial"])
        sb.assert_result_ok(result)
        assert "Serial drivers uninstalled" in result.output


def test_drivers_windows_only(apio_runner: ApioRunner):
    """Tests the 'apio drivers' commands on a windows platform."""

    # -- Skip this test if not running on a windows platform
    if not apio_platforms.get_apio_platform().is_windows:
        pytest.skip("Windows only test")

    with apio_runner.in_sandbox():

        # TODO: Find a creative way to test 'something' here. Maybe using
        # a 'dry-run' option that will skip dispatching zadig and the
        # serial installer and will just print the instructions to the
        # user.
        pass
