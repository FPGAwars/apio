"""
Test different "apio" commands
"""

import os
from os.path import getsize
from test.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_examples(apio_runner: ApioRunner):
    """Tests the listing and fetching apio examples."""

    with apio_runner.in_sandbox() as sb:

        # -- 'apio examples list'
        result = sb.invoke_apio_cmd(apio, ["examples", "list"])
        sb.assert_ok(result)
        assert "alhambra-ii/ledon" in result.output
        assert "Turning on a led" in result.output

        # -- 'apio examples fetch alhambra-ii/ledon' (colors off)
        result = sb.invoke_apio_cmd(
            apio,
            ["examples", "fetch", "alhambra-ii/ledon"],
            terminal_mode=False,
        )
        sb.assert_ok(result)
        assert "Copying alhambra-ii/ledon example files" in result.output
        assert (
            "Example 'alhambra-ii/ledon' fetched successfully" in result.output
        )
        assert getsize("apio.ini")
        assert getsize("ledon.v")

        # -- 'apio examples fetch alhambra-ii' (colors off)
        os.makedirs("temp", exist_ok=False)
        os.chdir("temp")
        result = sb.invoke_apio_cmd(
            apio,
            ["examples", "fetch", "alhambra-ii"],
            terminal_mode=False,
        )
        sb.assert_ok(result)
        assert "Fetching alhambra-ii/blinky" in result.output
        assert "Fetching alhambra-ii/ledon" in result.output
        assert "Examples fetched successfully" in result.output
        assert getsize("ledon/ledon.v")
        os.chdir("..")

        # -- 'apio examples fetch alhambra-ii/ledon -d dir1' (colors off)
        result = sb.invoke_apio_cmd(
            apio,
            ["examples", "fetch", "alhambra-ii/ledon", "-d", "dir1"],
            terminal_mode=False,
        )
        sb.assert_ok(result)
        assert "Copying alhambra-ii/ledon example files" in result.output
        assert (
            "Example 'alhambra-ii/ledon' fetched successfully" in result.output
        )
        assert getsize("dir1/ledon.v")

        # -- 'apio examples fetch alhambra -d dir2 (colors off)
        result = sb.invoke_apio_cmd(
            apio,
            ["examples", "fetch", "alhambra-ii", "-d", "dir2"],
            terminal_mode=False,
        )
        sb.assert_ok(result)
        assert "Examples fetched successfully" in result.output
        assert getsize("dir2/ledon/ledon.v")
