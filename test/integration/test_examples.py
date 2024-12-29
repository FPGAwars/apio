"""
  Test different "apio" commands
"""

import os
from os.path import getsize
from test.conftest import ApioRunner
import pytest
from apio.commands.apio import cli as apio


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_examples(apio_runner: ApioRunner):
    """Tests the listing and fetching apio examples."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    with apio_runner.in_sandbox() as sb:

        # -- Install the examples package.
        result = sb.invoke_apio_cmd(apio, ["packages", "install", "examples"])
        sb.assert_ok(result)
        assert "Package 'examples' installed successfully" in result.output
        assert getsize(sb.packages_dir / "examples/alhambra-ii/ledon/ledon.v")

        # -- 'apio examples list'
        result = sb.invoke_apio_cmd(apio, ["examples", "list"])
        sb.assert_ok(result)
        assert "alhambra-ii/ledon" in result.output
        assert "Hello world for the Alhambra-II board" in result.output

        # -- 'apio examples fetch alhambra-ii/ledon'
        result = sb.invoke_apio_cmd(
            apio,
            ["examples", "fetch", "alhambra-ii/ledon"],
        )
        sb.assert_ok(result)
        assert "Copying alhambra-ii/ledon example files" in result.output
        assert (
            "Fetched successfully the files of example "
            "'alhambra-ii/ledon'" in result.output
        )
        assert getsize("ledon.v")

        # -- 'apio examples fetch-board alhambra-ii'
        result = sb.invoke_apio_cmd(
            apio,
            ["examples", "fetch-board", "alhambra-ii"],
        )
        sb.assert_ok(result)
        assert "Creating directory alhambra-ii" in result.output
        assert "has been fetched successfully" in result.output
        assert getsize("alhambra-ii/ledon/ledon.v")

        # -- 'apio examples fetch alhambra-ii/ledon -d dir1'
        result = sb.invoke_apio_cmd(
            apio,
            ["examples", "fetch", "alhambra-ii/ledon", "-d", "dir1"],
        )
        sb.assert_ok(result)
        assert "Copying alhambra-ii/ledon example files" in result.output
        assert (
            "Fetched successfully the files of example "
            "'alhambra-ii/ledon'" in result.output
        )
        assert getsize("dir1/ledon.v")

        # -- 'apio examples fetch-board alhambra -d dir2
        result = sb.invoke_apio_cmd(
            apio,
            ["examples", "fetch-board", "alhambra-ii", "-d", "dir2"],
        )
        sb.assert_ok(result)
        assert f"Creating directory dir2{os.sep}alhambra-ii" in result.output
        assert (
            "Board 'alhambra-ii' examples has been fetched "
            "successfully" in result.output
        )
        assert getsize("dir2/alhambra-ii/ledon/ledon.v")
