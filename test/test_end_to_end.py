"""
  Test different "apio" commands
"""

import pathlib

import pytest

# -- Entry point for apio commands.
from apio.commands.packages import cli as cmd_packages
from apio.commands.create import cli as cmd_create
from apio.commands.upload import cli as cmd_upload
from apio.commands.examples import cli as cmd_examples


def validate_files_leds(folder):
    """Check that the ledon.v file is inside the given folder"""

    # -- File to check
    leds = folder / pathlib.Path("ledon.v")

    # -- The file should exists and have a size greather than 0
    assert leds.exists() and leds.stat().st_size > 0  # getsize(leds) > 0


def validate_dir_leds(folder=""):
    """Check that the leds folder has been created in the
    dir directory
    """

    # -- Get the leds path
    leds_dir = folder / pathlib.Path("Alhambra-II/ledon")

    # -- Calculate the numer of files in the leds folder
    nfiles = len(list(leds_dir.glob("*")))

    # -- The folder should exist, and it should
    # -- containe more than 0 files inside
    assert leds_dir.is_dir() and nfiles > 0


def test_end_to_end1(
    click_cmd_runner, assert_apio_cmd_ok, setup_apio_test_env, offline_flag
):
    """Test the installation of the examples package"""

    # -- If the option 'offline' is passed, the test is skip
    # -- (These tests require internet)
    if offline_flag:
        pytest.skip("requires internet connection")

    with click_cmd_runner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        setup_apio_test_env()

        # -- Execute "apio packages --uninstall examples"
        result = click_cmd_runner.invoke(
            cmd_packages, ["--uninstall", "examples"], input="y"
        )
        assert "Do you want to uninstall 1 package?" in result.output
        assert "Package 'examples' was not installed" in result.output

        # -- Execute "apio packages --install examples@X"
        result = click_cmd_runner.invoke(
            cmd_packages, ["--install", "examples@X"]
        )
        assert "Error: package not found" in result.output

        # -- Execute "apio packages --install examples@0.0.34"
        result = click_cmd_runner.invoke(
            cmd_packages, ["--install", "examples@0.0.34"]
        )
        assert_apio_cmd_ok(result)
        assert "Installing package 'examples@" in result.output
        assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output

        # -- Execute "apio packages --install examples"
        result = click_cmd_runner.invoke(
            cmd_packages, ["--install", "examples"]
        )
        assert_apio_cmd_ok(result)
        assert "Installing package 'examples'" in result.output
        assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output

        # -- Execute "apio packages --install examples" again
        result = click_cmd_runner.invoke(
            cmd_packages, ["--install", "examples"]
        )
        assert_apio_cmd_ok(result)
        assert "Installing package 'examples'" in result.output
        assert "was already installed" in result.output

        # -- Execute "apio packages --install examples --force"
        result = click_cmd_runner.invoke(
            cmd_packages,
            [
                "--install",
                "examples",
                "--force",
            ],
        )
        assert_apio_cmd_ok(result)
        assert "Installing package 'examples'" in result.output
        assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output

        # -- Execute "apio packages --list"
        result = click_cmd_runner.invoke(cmd_packages, ["--list"])
        assert result.exit_code == 0, result.output
        assert "No errors" in result.output
        assert "Installed packages:" in result.output
        assert "examples" in result.output


def test_end_to_end2(
    click_cmd_runner, assert_apio_cmd_ok, setup_apio_test_env, offline_flag
):
    """Test more 'apio examples' commands"""

    # -- If the option 'offline' is passed, the test is skip
    # -- (These tests require internet)
    if offline_flag:
        pytest.skip("requires internet connection")

    with click_cmd_runner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        setup_apio_test_env()

        # -- Execute "apio create --board alhambra-ii"
        result = click_cmd_runner.invoke(
            cmd_create, ["--board", "alhambra-ii"]
        )
        assert_apio_cmd_ok(result)
        assert "Creating apio.ini file ..." in result.output
        assert "was created successfully" in result.output

        # -- Execute "apio upload"
        result = click_cmd_runner.invoke(cmd_upload)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output

        # -- Execute "apio packages --install examples"
        result = click_cmd_runner.invoke(
            cmd_packages, ["--install", "examples"]
        )
        assert_apio_cmd_ok(result)
        assert "Installing package 'examples'" in result.output
        assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output

        # -- Execute "apio examples --list"
        result = click_cmd_runner.invoke(cmd_examples, ["--list"])
        assert_apio_cmd_ok(result)
        assert "leds" in result.output
        assert "icezum" in result.output

        # -- Execute "apio examples --fetch-files missing_example"
        result = click_cmd_runner.invoke(
            cmd_examples, ["--fetch-files", "missing_example"]
        )
        assert result.exit_code == 1, result.output
        assert "Warning: this example does not exist" in result.output

        # -- Execute "apio examples --fetch-files Alhambra-II/ledon"
        result = click_cmd_runner.invoke(
            cmd_examples, ["--fetch-files", "Alhambra-II/ledon"]
        )
        assert_apio_cmd_ok(result)
        assert "Copying Alhambra-II/ledon example files ..." in result.output
        assert "have been successfully created!" in result.output
        validate_files_leds(pathlib.Path())

        # -- Execute "apio examples --fetch-dir Alhambra-II/ledon"
        result = click_cmd_runner.invoke(
            cmd_examples, ["--fetch-dir", "Alhambra-II/ledon"]
        )
        assert_apio_cmd_ok(result)
        assert "Creating Alhambra-II/ledon directory ..." in result.output
        assert "has been successfully created" in result.output
        validate_dir_leds()

        # -- Execute "apio examples --fetch-dir Alhambra-II/ledon"
        result = click_cmd_runner.invoke(
            cmd_examples, ["--fetch-dir", "Alhambra-II/ledon"], input="y"
        )
        assert_apio_cmd_ok(result)
        assert (
            "Warning: Alhambra-II/ledon directory already exists"
            in result.output
        )
        assert "Do you want to replace it?" in result.output
        assert "Creating Alhambra-II/ledon directory ..." in result.output
        assert "has been successfully created" in result.output
        validate_dir_leds()


def test_end_to_end3(
    click_cmd_runner, assert_apio_cmd_ok, setup_apio_test_env, offline_flag
):
    """Test more 'apio examples' commands"""

    # -- If the option 'offline' is passed, the test is skip
    # -- (These tests require internet)
    if offline_flag:
        pytest.skip("requires internet connection")

    with click_cmd_runner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        setup_apio_test_env()

        # -- Execute "apio packages --install examples"
        result = click_cmd_runner.invoke(
            cmd_packages, ["--install", "examples"]
        )
        assert_apio_cmd_ok(result)
        assert "Installing package 'examples'" in result.output
        assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output

        # ------------------------------------------
        # -- Check the --project-dir parameter
        # ------------------------------------------
        # -- Create a tmp dir
        p = pathlib.Path("tmp/")
        p.mkdir(parents=True, exist_ok=True)

        # -- Execute "apio examples --fetch-files Alhambra-II/ledon
        # --                        --project-dir=tmp"
        result = click_cmd_runner.invoke(
            cmd_examples,
            ["--fetch-files", "Alhambra-II/ledon", "--project-dir=tmp"],
        )
        assert_apio_cmd_ok(result)
        assert "Copying Alhambra-II/ledon example files ..." in result.output
        assert "have been successfully created!" in result.output

        # -- Check the files in the tmp folder
        validate_files_leds(p)

        # -- Execute
        # -- "apio examples --fetch-dir Alhambra-II/ledon --project-dir=tmp"
        result = click_cmd_runner.invoke(
            cmd_examples,
            ["--fetch-dir", "Alhambra-II/ledon", "--project-dir=tmp"],
        )
        assert_apio_cmd_ok(result)
        assert "Creating Alhambra-II/ledon directory ..." in result.output
        assert "has been successfully created" in result.output
        validate_dir_leds("tmp")

        # -- Execute "apio packages --uninstall examples"
        result = click_cmd_runner.invoke(
            cmd_packages, ["--uninstall", "examples"], input="n"
        )
        assert result.exit_code != 0, result.output
        assert "User said no" in result.output

        # -- Execute "apio packages --uninstall examples"
        result = click_cmd_runner.invoke(
            cmd_packages, ["--uninstall", "examples"], input="y"
        )
        assert_apio_cmd_ok(result)
        assert "Uninstalling package 'examples'" in result.output
        assert "Do you want to uninstall 1 package?" in result.output
        assert "Package 'examples' uninstalled successfuly" in result.output
