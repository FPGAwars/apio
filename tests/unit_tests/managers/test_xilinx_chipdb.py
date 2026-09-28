"""Tests for the openxc7 parts-index lookup."""

from pathlib import Path
import pytest
from tests.conftest import ApioRunner
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.managers.xilinx_chipdb import (
    chipdb_file_for_part,
    _read_xilinx_parts_index,
)


def test_find_chipdb_ok(apio_runner: ApioRunner):
    """Tests the case where the part is generated."""

    with apio_runner.in_sandbox():

        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        chipdb_file_path = chipdb_file_for_part(apio_ctx, "xc7a35tcsg324-1")
        assert chipdb_file_path.is_file(), chipdb_file_path

        expected_path = (
            apio_ctx.get_package_dir("openxc7")
            / "chipdb"
            / "chipdb-xc7a50t.bin"
        )
        assert chipdb_file_path == expected_path


def test_find_chipdb_non_generated(apio_runner: ApioRunner):
    """Tests the case where the part is not generated."""

    with apio_runner.in_sandbox():

        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                chipdb_file_for_part(apio_ctx, "xc7s100fgga484-1")
        assert e.value.code == 1
        assert "part xc7s100fgga484-1 exists but not generated" in log.out


def test_find_chipdb_no_such_part(apio_runner: ApioRunner):
    """Tests the case where the part does not exist."""

    with apio_runner.in_sandbox():

        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                chipdb_file_for_part(apio_ctx, "xc7s999999999-1")
        assert e.value.code == 1
        assert "No such xilinx yosys part xc7s999999999-1" in log.out


def test_old_schema_is_rejected(apio_runner: ApioRunner):
    """Test that a xilinx part index with old schema number is rejected."""

    with apio_runner.in_sandbox() as sb:

        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        # -- Read the xilinx parts list
        json_data = sb.read_json_file(
            apio_ctx.get_package_dir("openxc7") / "XILINX-PARTS-INDEX.json"
        )
        schema_version = json_data["schema"]
        assert isinstance(schema_version, int)

        # -- Write the parts list to a local file with and old schema version.
        assert schema_version != 6
        json_data["schema"] = 6
        local_index_path = Path("local_index.json")
        sb.write_json_file(local_index_path, json_data)

        # -- Reading the local index should fail.
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                _read_xilinx_parts_index(local_index_path)
        assert e.value.code == 1
        assert "Error: Unexpected schema version 6" in log.out
