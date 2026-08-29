"""A manager class for  to dispatch the Apio SCONS targets."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

# TODO: Add test coverage.


from pathlib import Path
from apio.common.apio_console import cout
from apio.apio_context import ApioContext
from apio.managers.downloader import FileDownloader
from apio.managers.unpacker import FileUnpacker


def chipdb_file_on_demand(
    apio_ctx: ApioContext,
    xilinx_chip: str,
    chipdb_dir: Path,
):
    """Called to insure that the chipdb file for the given xilinx chip id
    exists. If not, it is being downloaded on the fly."""

    # -- TODO: This is a proof of concept code. Clean up.

    chipdb_file_name = xilinx_chip + ".bin"
    chipdb_file = chipdb_dir / chipdb_file_name
    if chipdb_file.exists():
        cout(f"Chipdb file found: {chipdb_file_name}")
        return

    package_install_info = apio_ctx.package_manager.installed_packages[
        "openxc7"
    ]
    package_url = package_install_info["loaded-from"]
    release_tag = package_install_info["version"].replace(".", "")
    chipdb_tgz = (
        "apio-xilinx-chipdb-" + xilinx_chip + "-" + release_tag + ".bin.tgz"
    )
    chipdb_url = package_url.rsplit("/", 1)[0] + "/" + chipdb_tgz
    cout(f"Fetching {chipdb_tgz}")
    downloader = FileDownloader(chipdb_url, chipdb_dir)
    downloader.start()
    unpacker = FileUnpacker(chipdb_dir / chipdb_tgz, chipdb_dir)
    ok = unpacker.start()
    assert ok
    assert chipdb_file.exists(), chipdb_file
