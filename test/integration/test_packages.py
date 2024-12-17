"""
  Test different "apio" commands
"""

from os import listdir, chdir
from test.conftest import ApioRunner
import pytest

# -- Entry point for apio commands.
from apio.commands.packages import cli as apio_packages


# R0801: Similar lines in 2 files
# pylint: disable=R0801
# # R0915: Too many statements (52/50) (too-many-statements)
# # pylint: disable=R0915
def test_packages(apio_runner: ApioRunner):
    """Tests listing, installation and uninstallation of packages."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    with apio_runner.in_sandbox() as sb:

        # -- Create and change to project dir.
        sb.proj_dir.mkdir()
        chdir(sb.proj_dir)

        # -- List packages
        result = sb.invoke_apio_cmd(apio_packages, ["--list"])
        assert result.exit_code == 0
        assert "No errors" in result.output
        assert "examples" in result.output
        assert "oss-cad-suite" in result.output

        # -- Packages dir doesn't exist yet.
        assert not sb.packages_dir.exists()

        # -- Install the examples package. Package 'examples' should exist,
        # -- and package 'tools-oss-cad-suite' should not.
        result = sb.invoke_apio_cmd(apio_packages, ["--install", "examples"])
        sb.assert_ok(result)
        assert "Package 'examples' installed successfully" in result.output
        assert listdir(sb.packages_dir / "examples/examples/alhambra-ii")
        assert "tools-oss-cad-suite" not in listdir(sb.packages_dir)

        # -- Install the reset of the packages.
        # -- Both 'examples' and 'tools-oss-cad-suite' should exist, and
        # -- maybe others, depending on the platform.
        result = sb.invoke_apio_cmd(apio_packages, ["--install"])
        sb.assert_ok(result)
        assert "Package 'examples' installed successfully" not in result.output
        assert (
            "Package 'oss-cad-suite' installed successfully" in result.output
        )
        assert listdir(sb.packages_dir / "examples/examples/alhambra-ii")
        assert listdir(sb.packages_dir / "tools-oss-cad-suite/bin")

        # -- Delete a file from the examples package, we will use it as an
        # -- indicator for the reinstallation of the package.
        marker_file = (
            sb.packages_dir / "examples/examples/alhambra-ii/ledon/ledon.v"
        )
        assert marker_file.is_file()
        marker_file.unlink()
        assert not marker_file.exists()

        # -- Install the examples packages without forcing.
        # -- This should not do anything since it's considered to be installed.
        result = sb.invoke_apio_cmd(apio_packages, ["--install", "examples"])
        sb.assert_ok(result)
        assert "was already install" in result.output
        assert "Package 'examples' installed" not in result.output
        assert not marker_file.exists()

        # -- Install the examples packages with forcing.
        # -- This should recover the file.
        result = sb.invoke_apio_cmd(
            apio_packages, ["--install", "--force", "examples"]
        )
        sb.assert_ok(result)
        assert "Package 'examples' installed" in result.output
        assert marker_file.is_file()

        # -- Try to uninstall the 'examples' package without user approval.
        # -- should exit with an error message.
        assert "examples" in listdir(sb.packages_dir)
        result = sb.invoke_apio_cmd(
            apio_packages, ["--uninstall", "examples"], input="n"
        )
        assert result.exit_code == 1
        assert "User said no" in result.output
        assert "examples" in listdir(sb.packages_dir)
        assert "tools-oss-cad-suite" in listdir(sb.packages_dir)

        # -- Uninstall the examples package. It should delete the exemples
        # -- package and will live the rest.
        assert "examples" in listdir(sb.packages_dir)
        result = sb.invoke_apio_cmd(
            apio_packages, ["--uninstall", "examples"], input="y"
        )
        sb.assert_ok(result)
        assert "examples" not in listdir(sb.packages_dir)
        assert "tools-oss-cad-suite" in listdir(sb.packages_dir)

        # -- Uninstall all packages. This should uninstall also the
        # -- oss-cad-suite package.
        result = sb.invoke_apio_cmd(apio_packages, ["--uninstall", "--sayyes"])
        sb.assert_ok(result)
        assert "examples" not in listdir(sb.packages_dir)
        assert "tools-oss-cad-suite" not in listdir(sb.packages_dir)
