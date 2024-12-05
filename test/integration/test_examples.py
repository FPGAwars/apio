"""
  Test different "apio" commands
"""

from os import chdir
from os.path import getsize
from test.conftest import ApioRunner
import pytest

# -- Entry point for apio commands.
from apio.commands.packages import cli as apio_packages
from apio.commands.examples import cli as apio_examples


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_examples(apio_runner: ApioRunner):
    """Tests the listing and fetching apio examples."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    with apio_runner.in_sandbox() as sb:

        # -- Create and change to project dir.
        sb.proj_dir.mkdir()
        chdir(sb.proj_dir)

        # -- Install the examples package.
        result = sb.invoke_apio_cmd(apio_packages, ["--install", "examples"])
        sb.assert_ok(result)
        # assert "Installing package 'examples'" in result.output
        # assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output
        assert getsize(sb.packages_dir / "examples/alhambra-ii/ledon/ledon.v")

        # -- List the examples
        result = sb.invoke_apio_cmd(
            apio_examples,
            ["--list"],
        )
        sb.assert_ok(result)
        assert "alhambra-ii/ledon" in result.output

        # -- Fetch example files to current directory
        result = sb.invoke_apio_cmd(
            apio_examples,
            ["--fetch-files", "alhambra-ii/ledon"],
        )
        sb.assert_ok(result)
        assert "Copying alhambra-ii/ledon example files" in result.output
        assert "have been successfully created!" in result.output
        assert getsize("ledon.v")

        # -- Fetch example dir to current directory
        result = sb.invoke_apio_cmd(
            apio_examples,
            ["--fetch-dir", "alhambra-ii/ledon"],
        )
        sb.assert_ok(result)
        assert "Creating alhambra-ii/ledon directory" in result.output
        assert "has been successfully created" in result.output
        assert getsize("alhambra-ii/ledon/ledon.v")

        # -- Fetch example files to another project dir
        result = sb.invoke_apio_cmd(
            apio_examples,
            ["--fetch-files", "alhambra-ii/ledon", "--project-dir=./dir1"],
        )
        sb.assert_ok(result)
        assert "Copying alhambra-ii/ledon example files" in result.output
        assert "have been successfully created!" in result.output
        assert getsize("dir1/ledon.v")

        # -- Fetch example dir to another project dir
        result = sb.invoke_apio_cmd(
            apio_examples,
            ["--fetch-dir", "alhambra-ii/ledon", "--project-dir=dir2"],
        )
        sb.assert_ok(result)
        assert "Creating alhambra-ii/ledon directory" in result.output
        assert "has been successfully created" in result.output
        assert getsize("dir2/alhambra-ii/ledon/ledon.v")
