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

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment
        proj_dir, _, packages_dir = apio_runner.setup_env()

        # -- Create and change to project dir.
        proj_dir.mkdir(exist_ok=False)
        chdir(proj_dir)

        # -- Install the examples package.
        result = apio_runner.invoke(apio_packages, ["--install", "examples"])
        apio_runner.assert_ok(result)
        # assert "Installing package 'examples'" in result.output
        # assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output
        assert getsize(packages_dir / "examples/Alhambra-II/ledon/ledon.v")

        # -- List the examples
        result = apio_runner.invoke(
            apio_examples,
            ["--list"],
        )
        apio_runner.assert_ok(result)
        assert "Alhambra-II/ledon" in result.output

        # -- Fetch example files to current directory
        result = apio_runner.invoke(
            apio_examples,
            ["--fetch-files", "Alhambra-II/ledon"],
        )
        apio_runner.assert_ok(result)
        assert "Copying Alhambra-II/ledon example files" in result.output
        assert "have been successfully created!" in result.output
        assert getsize("ledon.v")

        # -- Fetch example dir to current directory
        result = apio_runner.invoke(
            apio_examples,
            ["--fetch-dir", "Alhambra-II/ledon"],
        )
        apio_runner.assert_ok(result)
        assert "Creating Alhambra-II/ledon directory" in result.output
        assert "has been successfully created" in result.output
        assert getsize("Alhambra-II/ledon/ledon.v")

        # -- Fetch example files to another project dir
        result = apio_runner.invoke(
            apio_examples,
            ["--fetch-files", "Alhambra-II/ledon", "--project-dir=./dir1"],
        )
        apio_runner.assert_ok(result)
        assert "Copying Alhambra-II/ledon example files" in result.output
        assert "have been successfully created!" in result.output
        assert getsize("dir1/ledon.v")

        # -- Fetch example dir to another project dir
        result = apio_runner.invoke(
            apio_examples,
            ["--fetch-dir", "Alhambra-II/ledon", "--project-dir=dir2"],
        )
        apio_runner.assert_ok(result)
        assert "Creating Alhambra-II/ledon directory" in result.output
        assert "has been successfully created" in result.output
        assert getsize("dir2/Alhambra-II/ledon/ledon.v")
