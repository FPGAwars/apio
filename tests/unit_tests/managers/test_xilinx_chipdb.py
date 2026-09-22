"""Tests for the openxc7 parts-index reader."""

import json
import os

import pytest
from tests.conftest import ApioRunner, ApioSandbox
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.managers.xilinx_chipdb import (
    PARTS_INDEX_FILE_NAME,
    chipdb_file_on_demand,
    read_xilinx_parts_index,
)

_PART = "xc7a35tcsg324-1"


def _write_index(sb: ApioSandbox, document: dict) -> None:
    """Write a parts index under the sandbox home.

    The sandbox points APIO_PACKAGES at a shared cache. This test points
    it at the sandbox home instead, so the fixture does not touch that
    cache.
    """
    packages = sb.home_dir / "packages"
    os.environ["APIO_PACKAGES"] = str(packages)
    index_path = packages / "openxc7" / PARTS_INDEX_FILE_NAME
    sb.write_file(index_path, json.dumps(document))


def _context() -> ApioContext:
    """An apio context that does not install packages."""
    return ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.IGNORE_PACKAGES,
    )


def _entry() -> dict:
    """One generated part. Schema 6 has no pnr field."""
    return {
        "family": "artix7",
        "base-part": "xc7a35tcsg324",
        "speed": "1",
        "generated": True,
        "chipdb": "chipdb-xc7a35tcsg324.bin",
    }


def _document(parts: dict, schema: int = 6) -> dict:
    """A minimal parts index."""
    return {"schema": schema, "parts": parts}


def test_schema_6_is_accepted(apio_runner: ApioRunner):
    """A schema 6 index with no pnr field is accepted."""
    with apio_runner.in_sandbox() as sb:
        _write_index(sb, _document({_PART: _entry()}))
        apio_ctx = _context()
        document = read_xilinx_parts_index(apio_ctx)
        assert document["schema"] == 6
        assert _PART in document["parts"]
        assert "pnr" not in document["parts"][_PART]


def test_absent_part_is_fatal(apio_runner: ApioRunner):
    """A part that is not in the index is a fatal error naming it."""
    with apio_runner.in_sandbox() as sb:
        _write_index(sb, _document({"xc7a100tcsg324-1": _entry()}))
        apio_ctx = _context()
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                chipdb_file_on_demand(apio_ctx, _PART)
        assert e.value.code == 1
        assert _PART in log.out


def test_schema_5_is_rejected(apio_runner: ApioRunner):
    """A schema 5 index is rejected by the shared reader, including when
    the chipdb fetch is what opens it."""
    with apio_runner.in_sandbox() as sb:
        _write_index(sb, _document({_PART: _entry()}, schema=5))
        apio_ctx = _context()
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                read_xilinx_parts_index(apio_ctx)
        assert e.value.code == 1
        assert "expected 6" in log.out

        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                chipdb_file_on_demand(apio_ctx, _PART)
        assert e.value.code == 1
        assert "expected 6" in log.out
