"""A manager class for  to dispatch the Apio SCONS targets."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

# TODO: Add test coverage.

import sys
import json
from pathlib import Path
from apio.common.apio_console import cout, cerror
from apio.common.apio_styles import INFO, ERROR
from apio.apio_context import ApioContext
from apio.managers.downloader import FileDownloader
from apio.managers.unpacker import FileUnpacker
from apio.utils import util

EXPECTED_SCHEMA_VERSION = 5


def chipdb_file_on_demand(
    apio_ctx: ApioContext,
    yosys_part: str,
    # chipdb_dir: Path,
) -> Path:
    """Given a xilinx yosys-part, it fetches the chipdb file on demand and
    returns its path."""

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements

    # -- Get the local chipdb dir in the installed openxc7 package.
    # -- The path of this dir is defined in packages.jsonc.
    openxc7_define_consts = apio_ctx.all_packages["openxc7"]["env"][
        "define-consts"
    ]
    assert "CHIPDB_DIR" in openxc7_define_consts, openxc7_define_consts
    chipdb_dir = Path(openxc7_define_consts["CHIPDB_DIR"])

    # -- Delete all *.tgz files in the chipdb dir
    for path in chipdb_dir.glob("*.tgz"):
        cout(f"Deleting a leftover chipdb archive {path.name}", style=INFO)
        path.unlink()

    # -- Read the xilinx parts index at the root of the openxc7 package.
    openxc7_dir = apio_ctx.get_package_dir("openxc7")
    parts_index_path = openxc7_dir / "PARTS-INDEX.json"
    with open(parts_index_path, encoding="utf-8") as f:
        json_data = json.load(f)

    # -- Verify that the index has a schema we understand.
    actual_schema_version = (
        json_data["schema"] if "schema" in json_data else "Unknown"
    )
    if actual_schema_version != EXPECTED_SCHEMA_VERSION:
        cerror(
            f"Unexpected schema version {actual_schema_version}, "
            f"expected {EXPECTED_SCHEMA_VERSION}"
        )
        sys.exit(1)

    # -- Lookup information for the yosys_part.
    parts = json_data["parts"]
    if yosys_part not in parts:
        cerror(f"No such xilinx yosys part {yosys_part}")
        cout(
            f"See {str(parts_index_path)} for the list of "
            "supported xilinx parts.",
            style=INFO,
        )
        sys.exit(1)

    part_info = parts[yosys_part]

    if not part_info["generated"]:
        cerror(f"Yosys xilinx part {yosys_part} exists but not generated")
        cout("Ask the Apio team to generate it.", style=INFO)
        sys.exit(1)

    chipdb_file_name = part_info["chipdb"]
    asset_name = part_info["asset"]

    # -- If the chipdb file already exists then we are good, return with
    # -- the file path.
    chipdb_file_path = chipdb_dir / chipdb_file_name
    if chipdb_file_path.exists():
        cout(f"Chipdb file found: {chipdb_file_name}")
        actual_sha256 = util.compute_file_sha256(chipdb_file_path)
        expected_sha256 = part_info["chipdb-sha256"]
        if actual_sha256 == expected_sha256:
            return chipdb_file_path
        cout(
            "Existing chipdb file has an unexpected checksum: "
            f"{actual_sha256}",
            style=INFO,
        )
        cout(f"Deleting old chipdb file {chipdb_file_path.name}")
        chipdb_file_path.unlink()

    # -- The chipdb file doesn't exist, we need to fetch it from the
    # -- same release of the installed openxc7 package.
    package_install_info = apio_ctx.package_manager.installed_packages[
        "openxc7"
    ]
    package_url = package_install_info["loaded-from"]
    asset_url = package_url.rsplit("/", 1)[0] + "/" + asset_name

    # -- Fetch the asset.
    cout(f"Fetching {asset_name}")
    downloader = FileDownloader(asset_url, chipdb_dir)
    downloader.start()

    # -- Check the asset size and checksum
    local_asset = chipdb_dir / asset_name
    actual_sha256 = util.compute_file_sha256(local_asset)
    expected_sha256 = part_info["asset-sha256"]

    if actual_sha256 != expected_sha256:
        cerror(
            f"Downloaded chipdb asset has an unexpected checksum: "
            f"{actual_sha256}"
        )
        cout(f"Expected {expected_sha256}", style=ERROR)
        sys.exit(1)

    # -- Unpack the asset
    unpacker = FileUnpacker(local_asset, chipdb_dir)
    ok = unpacker.start()
    assert ok

    actual_sha256 = util.compute_file_sha256(chipdb_file_path)
    expected_sha256 = part_info["chipdb-sha256"]
    if actual_sha256 != expected_sha256:
        cerror(f"Chipdb file has an expected checksum {actual_sha256}")
        cout(f"Expected {expected_sha256}", style=ERROR)
        sys.exit(1)

    cout("Chipdb checksum verified.")

    # -- Delete the asset
    local_asset.unlink()

    # -- All done, return with the file path.
    return chipdb_file_path
