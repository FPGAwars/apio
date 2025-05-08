"""Test different "apio" commands."""

from os import listdir
from test.conftest import ApioRunner
import pytest
from apio.commands.apio import cli as apio


def test_packages(apio_runner: ApioRunner):
    """Tests listing, installation and uninstallation of packages."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    with apio_runner.in_sandbox() as sb:

        # -- List packages
        result = sb.invoke_apio_cmd(apio, "packages", "list")
        assert result.exit_code == 0
        assert "examples" in result.output
        assert "oss-cad-suite" in result.output

        # -- Packages dir doesn't exist yet.
        assert not sb.packages_dir.exists()

        # -- Install the examples package. Package 'examples' should exist,
        # -- and package 'oss-cad-suite' should not.
        result = sb.invoke_apio_cmd(apio, "packages", "install", "examples")
        sb.assert_ok(result)
        assert "Package 'examples' installed successfully" in result.output
        assert listdir(sb.packages_dir / "examples/alhambra-ii")
        assert "oss-cad-suite" not in listdir(sb.packages_dir)

        # -- Install the reset of the packages.
        # -- Both 'examples' and 'oss-cad-suite' should exist, and
        # -- maybe others, depending on the platform.
        result = sb.invoke_apio_cmd(apio, "packages", "install")
        sb.assert_ok(result)
        assert "Package 'examples' installed successfully" not in result.output
        assert (
            "Package 'oss-cad-suite' installed successfully" in result.output
        )
        assert listdir(sb.packages_dir / "examples/alhambra-ii")
        assert listdir(sb.packages_dir / "oss-cad-suite/bin")

        # -- Delete a file from the examples package, we will use it as an
        # -- indicator for the reinstallation of the package.
        marker_file = sb.packages_dir / "examples/alhambra-ii/ledon/ledon.v"
        assert marker_file.is_file()
        marker_file.unlink()
        assert not marker_file.exists()

        # -- Install the examples packages without forcing.
        # -- This should not do anything since it's considered to be installed.
        result = sb.invoke_apio_cmd(apio, "packages", "install", "examples")
        sb.assert_ok(result)
        assert "Package 'examples' installed" not in result.output
        assert not marker_file.exists()

        # -- Install the examples packages with forcing.
        # -- This should recover the file.
        result = sb.invoke_apio_cmd(
            apio, "packages", "install", "--force", "examples"
        )
        sb.assert_ok(result)
        assert "Package 'examples' installed" in result.output
        assert marker_file.is_file()

        # -- Uninstall the examples package. It should delete the examples
        # -- package and will leave the rest.
        assert "examples" in listdir(sb.packages_dir)
        result = sb.invoke_apio_cmd(apio, "packages", "uninstall", "examples")
        sb.assert_ok(result)
        assert "examples" not in listdir(sb.packages_dir)
        assert "oss-cad-suite" in listdir(sb.packages_dir)

        # -- Uninstall all packages. This should uninstall also the
        # -- oss-cad-suite package.
        result = sb.invoke_apio_cmd(apio, "packages", "uninstall")
        sb.assert_ok(result)
        assert "examples" not in listdir(sb.packages_dir)
        assert "oss-cad-suite" not in listdir(sb.packages_dir)
