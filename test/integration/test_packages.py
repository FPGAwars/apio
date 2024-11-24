"""
  Test different "apio" commands
"""

from os import listdir, chdir
import pytest

# -- Entry point for apio commands.
from apio.commands.packages import cli as apio_packages


# R0801: Similar lines in 2 files
# pylint: disable=R0801
# # R0915: Too many statements (52/50) (too-many-statements)
# # pylint: disable=R0915
def test_packages(
    click_cmd_runner,
    setup_apio_test_env,
    assert_apio_cmd_ok,
    offline_flag,
):
    """Tests listing, installation and uninstallation of packages."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if offline_flag:
        pytest.skip("requires internet connection")

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        proj_dir, _, packages_dir = setup_apio_test_env()

        # -- Create and change to project dir.
        proj_dir.mkdir(exist_ok=False)
        chdir(proj_dir)

        # -- List packages
        result = click_cmd_runner.invoke(apio_packages, ["--list"])
        assert result.exit_code == 0
        assert "No errors" in result.output
        assert "examples" in result.output
        assert "oss-cad-suite" in result.output

        # -- Packages dir doesn't exist yet.
        assert not packages_dir.exists()

        # -- Install the examples package. Package 'examples' should exist,
        # -- and package 'tools-oss-cad-suite' should not.
        result = click_cmd_runner.invoke(
            apio_packages, ["--install", "examples"]
        )
        assert_apio_cmd_ok(result)
        assert "Package 'examples' installed successfully" in result.output
        assert listdir(packages_dir / "examples/Alhambra-II")
        assert "tools-oss-cad-suite" not in listdir(packages_dir)

        # -- Install the reset of the packages.
        # -- Both 'examples' and 'tools-oss-cad-suite' should exist, and
        # -- maybe others, depending on the platform.
        result = click_cmd_runner.invoke(apio_packages, ["--install"])
        assert_apio_cmd_ok(result)
        assert "Package 'examples' installed successfully" not in result.output
        assert (
            "Package 'oss-cad-suite' installed successfully" in result.output
        )
        assert listdir(packages_dir / "examples/Alhambra-II")
        assert listdir(packages_dir / "tools-oss-cad-suite/bin")

        # -- Delete a file from the examples package, we will use it as an
        # -- indicator for the reinstallation of the package.
        marker_file = packages_dir / "examples/Alhambra-II/ledon/ledon.v"
        assert marker_file.is_file()
        marker_file.unlink()
        assert not marker_file.exists()

        # -- Install the examples packages without forcing.
        # -- This should not do anything since it's considered to be installed.
        result = click_cmd_runner.invoke(
            apio_packages, ["--install", "examples"]
        )
        assert_apio_cmd_ok(result)
        assert "was already install" in result.output
        assert "Package 'examples' installed" not in result.output
        assert not marker_file.exists()

        # -- Install the examples packages with forcing.
        # -- This should recover the file.
        result = click_cmd_runner.invoke(
            apio_packages, ["--install", "--force", "examples"]
        )
        assert_apio_cmd_ok(result)
        assert "Package 'examples' installed" in result.output
        assert marker_file.is_file()

        # -- Try to uninstall the 'examples' package without user approval.
        # -- should exit with an error message.
        assert "examples" in listdir(packages_dir)
        result = click_cmd_runner.invoke(
            apio_packages, ["--uninstall", "examples"], input="n"
        )
        assert result.exit_code == 1
        assert "User said no" in result.output
        assert "examples" in listdir(packages_dir)
        assert "tools-oss-cad-suite" in listdir(packages_dir)

        # -- Uninstall the examples package. It should delete the exemples
        # -- package and will live the rest.
        assert "examples" in listdir(packages_dir)
        result = click_cmd_runner.invoke(
            apio_packages, ["--uninstall", "examples"], input="y"
        )
        assert_apio_cmd_ok(result)
        assert "examples" not in listdir(packages_dir)
        assert "tools-oss-cad-suite" in listdir(packages_dir)

        # -- Uninstall all packages. This should uninstall also the
        # -- oss-cad-suite package.
        result = click_cmd_runner.invoke(
            apio_packages, ["--uninstall", "--sayyes"]
        )
        assert_apio_cmd_ok(result)
        assert "examples" not in listdir(packages_dir)
        assert "tools-oss-cad-suite" not in listdir(packages_dir)
