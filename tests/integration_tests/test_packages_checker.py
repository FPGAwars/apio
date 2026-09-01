"""
Test the package checking functionality. This is a sanity checker that is
implemented by packages.check_packages() and invoked from a few places.
"""

import os
import json
import shutil
from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_yosys_release_tag_mismatch(apio_runner: ApioRunner):
    """Test the verification that the apio 'oss-cad-suite' and 'openxc7'
    use the same Yosys release."""

    with apio_runner.in_sandbox() as sb:

        # -- Fetch an example, this also verifies that the apio packages are
        # -- installed.
        result = sb.invoke_apio_cmd(
            apio, ["examples", "fetch", "basys3/blinky"]
        )
        sb.assert_result_ok(result)

        # -- Make a copy of the packages dir so we don't disturb the original.
        # -- This is because the packages are cached and shared between tests.
        # -- We create the fake package dir under the private sandbox of this
        # -- test instance which is deleted at the end of the test.
        fake_packages_dir = sb.sandbox_dir / "fake_packages_dir"
        shutil.copytree(
            sb.packages_dir, fake_packages_dir, dirs_exist_ok=False
        )

        # -- Set the fake packages dir as the default packages dir for apio.
        # -- This env is also cleared automatically by conftest.py at the end
        # -- of this test.
        os.environ["APIO_PACKAGES"] = str(fake_packages_dir)

        # -- Modify of the 'yosys-release-tag' of the 'oss-cad-suite' to
        # -- create a fake mismatch.
        build_info_path = (
            fake_packages_dir / "oss-cad-suite" / "BUILD-INFO.json"
        )

        with open(build_info_path, encoding="utf-8") as f:
            build_info_data = json.load(f)

        build_info_data["yosys-release-tag"] = "2026-01-01"

        with open(build_info_path, "w", encoding="utf-8") as f:
            json.dump(build_info_data, f, indent=2)

        # -- Now run the apio build and it should check and fail on
        # -- yosys-release-tag mismatch, even if the build is already up to
        # -- date.
        result = sb.invoke_apio_cmd(apio, ["build"])
        assert result.exit_code == 1
        assert 'were built with different "yosys-release-tag"' in result.output
