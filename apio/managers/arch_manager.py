# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
"""Manages the FPGAs architectures parts indexes."""

# pylint: disable=duplicate-code

import json
from dataclasses import dataclass
from pathlib import Path
from apio.common.apio_console import fatal_error
from apio.common.proto_util import proto_from_json_dict, check_is_required
from apio.common.proto.stubs.apio_parts_indexes_pb2 import ApioPartEntry
from apio.common.proto.stubs.apio_common_pb2 import ApioArch


@dataclass(frozen=True)
class ArchManager:
    """Architecture specific functionality in the Apio main process (vs.
    the Scons process that is managed by the architectures plugins).
    """

    arch: ApioArch
    apio_packages_dir: Path

    @property
    def parts_index_package_name(self) -> str:
        """Returns the name of the Apio package with the parts index for
        this architecture."""
        match (self.arch):
            case ApioArch.xilinx:
                return "openxc7"
            case _:
                return "oss-cad-suite"

    @property
    def parts_index_file_name(self) -> str:
        """Return the parts index file name of the given arch."""
        return ApioArch.Name(self.arch).upper() + "-PARTS-INDEX.json"

    def parts_index_file_path(self) -> Path:
        """Return the parts index file name of the given arch."""
        return (
            self.apio_packages_dir
            / self.parts_index_package_name
            / self.parts_index_file_name
        )

    def read_parts_index_file(
        self, *, generated_only: bool = False
    ) -> dict[str, ApioPartEntry]:
        """Read the parts index of this architecture."""

        # pylint: disable=broad-exception-caught

        # -- Read and parse the json content.
        index_file_path = self.parts_index_file_path()
        try:
            jsonc_text = index_file_path.read_text(encoding="utf-8")
            json_dict = json.loads(jsonc_text)
        except Exception as e:
            fatal_error(
                f"Failed to read and parse parts index file {str(index_file_path)}",
                cause=e,
            )

        # -- Convert to dict of protos
        result: dict[str, ApioPartEntry] = {}
        for part_id, part_dict in json_dict["parts"].items():
            # -- Convert part index entry from json dict to proto
            part_proto = proto_from_json_dict(part_dict, ApioPartEntry)
            if part_proto is None:
                fatal_error(
                    f"Failed to proto parse part index entry {part_id}"
                )
            # -- Add if generated or all entries where requested.
            check_is_required(part_proto, "generated")
            if part_proto.generated or not generated_only:
                result[part_id] = part_proto

        # -- All done.
        return result

    @staticmethod
    def get_arch_managers(
        apio_packages_dir: Path,
    ) -> dict[ApioArch | int, "ArchManager"]:
        """Return a mapping of arch to ArchManager."""
        return {
            ApioArch.ice40: ArchManager(ApioArch.ice40, apio_packages_dir),
            ApioArch.ecp5: ArchManager(ApioArch.ecp5, apio_packages_dir),
            ApioArch.gowin: ArchManager(ApioArch.gowin, apio_packages_dir),
            ApioArch.xilinx: ArchManager(ApioArch.xilinx, apio_packages_dir),
        }
