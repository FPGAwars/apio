"""
  Test different "apio" commands
"""

from pathlib import Path
from os import listdir
from os.path import getsize

import pytest

# -- Entry point for apio commands.
from apio.commands.packages import cli as cmd_packages
from apio.commands.create import cli as cmd_create
from apio.commands.upload import cli as cmd_upload
from apio.commands.examples import cli as cmd_examples


def test_end_to_end_1(
    click_cmd_runner, assert_apio_cmd_ok, setup_apio_test_env, offline_flag
):
    """Test the installation of the examples package"""

    # -- If the option 'offline' is passed, the test is skip
    # -- (These tests require internet)
    if offline_flag:
        pytest.skip("requires internet connection")

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
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


def test_end_to_end_2(
    click_cmd_runner, assert_apio_cmd_ok, setup_apio_test_env, offline_flag
):
    """Test more 'apio examples' commands"""

    # -- If the option 'offline' is passed, the test is skip
    # -- (These tests require internet)
    if offline_flag:
        pytest.skip("requires internet connection")

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
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
        assert getsize("ledon.v")

        # -- Execute "apio examples --fetch-dir Alhambra-II/ledon"
        result = click_cmd_runner.invoke(
            cmd_examples, ["--fetch-dir", "Alhambra-II/ledon"]
        )
        assert_apio_cmd_ok(result)
        assert "Creating Alhambra-II/ledon directory ..." in result.output
        assert "has been successfully created" in result.output
        assert listdir("Alhambra-II/ledon")

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
        assert listdir("Alhambra-II/ledon")


def test_examples_package(
    click_cmd_runner,
    assert_apio_cmd_ok,
    setup_apio_test_env,
    apio_packages_dir,
    offline_flag,
):
    """Test installation, use, and uninstallation of the 'examples' package."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (These tests require internet)
    if offline_flag:
        pytest.skip("requires internet connection")

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Tests starts with packages dir non existing.
        assert not apio_packages_dir().exists()

        # -- Execute "apio packages --install examples"
        result = click_cmd_runner.invoke(
            cmd_packages, ["--install", "examples"]
        )
        assert_apio_cmd_ok(result)
        assert "Installing package 'examples'" in result.output
        assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output
        assert getsize(
            apio_packages_dir() / "examples/Alhambra-II/ledon/ledon.v"
        )

        # ------------------------------------------
        # -- Check the --project-dir parameter
        # ------------------------------------------
        # -- Create a tmp dir
        tmp_dir = Path("tmp")
        tmp_dir.mkdir(parents=False, exist_ok=False)

        # -- Execute "apio examples --fetch-files Alhambra-II/ledon
        # --                        --project-dir=tmp"
        result = click_cmd_runner.invoke(
            cmd_examples,
            ["--fetch-files", "Alhambra-II/ledon", "--project-dir=tmp"],
        )
        assert_apio_cmd_ok(result)
        assert "Copying Alhambra-II/ledon example files ..." in result.output
        assert "have been successfully created!" in result.output
        assert getsize(tmp_dir / "ledon.v")

        # -- Execute
        # -- "apio examples --fetch-dir Alhambra-II/ledon --project-dir=tmp"
        result = click_cmd_runner.invoke(
            cmd_examples,
            ["--fetch-dir", "Alhambra-II/ledon", "--project-dir=tmp"],
        )
        assert_apio_cmd_ok(result)
        assert "Creating Alhambra-II/ledon directory ..." in result.output
        assert "has been successfully created" in result.output
        assert getsize(tmp_dir / "Alhambra-II/ledon/ledon.v")

        # -- Execute "apio packages --uninstall examples" and say no.
        result = click_cmd_runner.invoke(
            cmd_packages, ["--uninstall", "examples"], input="n"
        )
        assert result.exit_code != 0, result.output
        assert "User said no" in result.output
        assert getsize(
            apio_packages_dir() / "examples/Alhambra-II/ledon/ledon.v"
        )

        # -- Execute "apio packages --uninstall examples"
        result = click_cmd_runner.invoke(
            cmd_packages, ["--uninstall", "examples"], input="y"
        )
        assert_apio_cmd_ok(result)
        assert "Uninstalling package 'examples'" in result.output
        assert "Do you want to uninstall 1 package?" in result.output
        assert "Package 'examples' uninstalled successfuly" in result.output

        # -- Packages dir should be empty now.
        assert not listdir(apio_packages_dir())
