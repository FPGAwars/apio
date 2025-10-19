"""Test different "apio" commands."""

from os import listdir, rename
from test.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_packages(apio_runner: ApioRunner):
    """Tests listing, installation and uninstallation of packages."""

    # -- This is a slow test. Skip it if running with --fast-only flag.
    apio_runner.skip_test_if_fast_only()

    with apio_runner.in_sandbox() as sb:

        # -- Clear packages
        sb.clear_packages()
        assert not sb.packages_dir.exists()

        # -- Run 'apio packages list'
        result = sb.invoke_apio_cmd(apio, ["packages", "list"])
        assert result.exit_code == 0
        assert "Package 'examples' installed successfully" in result.output
        assert (
            "Package 'oss-cad-suite' installed successfully" in result.output
        )
        assert "examples" in result.output
        assert "oss-cad-suite" in result.output

        # -- Run 'apio packages update'.
        # -- Both 'examples' and 'oss-cad-suite' should exist, and
        # -- possibly others, depending on the platform.
        result = sb.invoke_apio_cmd(apio, ["packages", "update"])
        sb.assert_ok(result)
        assert "All Apio packages are installed OK" in result.output
        assert listdir(sb.packages_dir / "definitions")
        assert listdir(sb.packages_dir / "examples/alhambra-ii")
        assert listdir(sb.packages_dir / "oss-cad-suite/bin")

        # -- Delete a file from the examples package, we will use it as an
        # -- indicator for the reinstallation of the package.
        marker_file = sb.packages_dir / "examples/alhambra-ii/ledon/ledon.v"
        assert marker_file.is_file()
        marker_file.unlink()
        assert not marker_file.exists()

        # -- Run 'apio packages update'.
        # -- This should not do anything since it's considered to be installed.
        result = sb.invoke_apio_cmd(apio, ["packages", "update"])
        sb.assert_ok(result)
        assert "Package 'examples' installed" not in result.output
        assert not marker_file.exists()

        # -- Run 'apio packages update --force'
        # -- This should recover the file.
        result = sb.invoke_apio_cmd(apio, ["packages", "update", "--force"])
        sb.assert_ok(result)
        assert "Package 'examples' installed" in result.output
        assert marker_file.is_file()

        # -- Break the examples package by renaming it. This also creates an
        # -- orphan dir.
        example_package_dir = sb.packages_dir / "examples"
        bad_package_dir = sb.packages_dir / "unknown-package"
        rename(example_package_dir, bad_package_dir)
        assert not example_package_dir.exists()
        assert bad_package_dir.is_dir()

        # -- Run 'apio packages update'. This should fix everything.
        result = sb.invoke_apio_cmd(apio, ["packages", "update"])
        sb.assert_ok(result)
        assert "Uninstalling broken package 'examples'" in result.output
        assert (
            "Deleting unknown package dir 'unknown-package'" in result.output
        )
        assert "Package 'examples' installed successfully" in result.output
        assert example_package_dir.is_dir()
        assert marker_file.exists()
        assert not bad_package_dir.exists()
