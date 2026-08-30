"""The apio definitions manager class. This class manages the standard
and custom boards, fpgas, and programmers definitions."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2


import sys
import re
from pathlib import Path
from typing import Dict, Set, Tuple, Optional
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import json5
from apio.utils import proto_util
from apio.common.apio_console import cout, cerror
from apio.common.proto.apio_definitions_pb2 import (
    BoardDefinition,
    FpgaDefinition,
)

# -- Boards definitions file name.
BOARDS_JSONC = "boards.jsonc"

# -- FPGAs definitions file name.
FPGAS_JSONC = "fpgas.jsonc"

# -- Programmers definitions file name.
PROGRAMMERS_JSONC = "programmers.jsonc"

# -- A regex for validating boards, fpgas, and programmers ids.
ID_FORMAT = re.compile(r"^[a-z][a-z0-9-]*$")


# -- JSON schema for validating a single fpga definition in fpga.jsonc.
# -- The fields 'part-num' and 'size' are for information only.
FPGA_SCHEMA = schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "part-num": {"type": "string"},
        "arch": {
            "type": "string",
            "enum": ["ice40", "ecp5", "gowin", "xilinx"],
        },
        "size": {"type": "string"},
        "ice40-params": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "package": {"type": "string"},
            },
            "required": ["type", "package"],
            "additionalProperties": False,
        },
        "ecp5-params": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "package": {"type": "string"},
                "speed": {"type": "string"},
            },
            "required": ["type", "package", "speed"],
            "additionalProperties": False,
        },
        "gowin-params": {
            "type": "object",
            "properties": {
                "yosys-family": {"type": "string"},
                "nextpnr-family": {"type": "string"},
                "packer-device": {"type": "string"},
            },
            "required": ["yosys-family", "nextpnr-family", "packer-device"],
            "additionalProperties": False,
        },
        "xilinx-params": {
            "type": "object",
            "properties": {
                "family": {"type": "string"},
                "yosys-arch": {"type": "string"},
                "package": {"type": "string"},
                "speed": {"type": "string"},
            },
            "required": ["family", "yosys-arch", "package", "speed"],
            "additionalProperties": False,
        },
    },
    "required": ["part-num", "arch", "size"],
    "additionalProperties": False,
}


# -- JSON schema for validating a single programmer definition in
# -- programmers.jsonc.
PROGRAMMER_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["command", "args"],
    "properties": {"command": {"type": "string"}, "args": {"type": "string"}},
    "additionalProperties": False,
}


class ApioDefinitions:
    """Contains the apio definitions in the form of json dictionaries."""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-locals

    def __init__(
        self,
        package_definitions_dir: Path,
        project_definitions_dir: Optional[Path],
    ):

        # pylint: disable=too-many-branches

        assert isinstance(package_definitions_dir, Path)
        assert project_definitions_dir is None or isinstance(
            project_definitions_dir, Path
        )

        self._package_definitions_dir = package_definitions_dir
        self._project_definitions_dir = project_definitions_dir

        # -- Read boards definitions.
        boards_json, self.custom_boards_ids = self._load_definitions(
            BOARDS_JSONC,
            self._package_definitions_dir,
            self._project_definitions_dir,
        )

        # -- Convert the board definition dicts to BoardDefinition protos.
        self.boards: Dict[str, BoardDefinition] = {}
        for board_id, definition_dict in boards_json.items():
            definition = proto_util.proto_from_json_dict(
                definition_dict,
                BoardDefinition,
                f"Failed to parse board definition '{board_id}",
            )
            self.boards[board_id] = definition

        # -- Validate boards definitions. Optional project custom definition
        # -- supersede apio standard definitions.
        for board_id in self.boards:
            if not ID_FORMAT.match(board_id):
                cerror(f"Board id has an invalid format: {board_id}")
                sys.exit(1)

        # -- Read fpgas definitions.
        fpgas_json, self.custom_fpgas_ids = self._load_definitions(
            FPGAS_JSONC,
            self._package_definitions_dir,
            self._project_definitions_dir,
        )

        # -- Convert the fpgas definition dicts to FpgasDefinition protos.
        self.fpgas: Dict[str, FpgaDefinition] = {}
        for fpga_id, definition_dict in fpgas_json.items():
            definition = proto_util.proto_from_json_dict(
                definition_dict,
                FpgaDefinition,
                f"Failed to parse fpga definition '{fpga_id}",
            )
            self.fpgas[fpga_id] = definition

        # -- Validate fpgas definitions.
        for fpga_id, fpga_definition in self.fpgas.items():
            if not ID_FORMAT.match(fpga_id):
                cerror(f"FPGA id has an invalid format: {fpga_id}")
                sys.exit(1)
            part_num = fpga_definition.part_num
            lc_part_num = part_num.lower().replace("/", "-")
            if fpga_id != lc_part_num and not fpga_id.startswith(
                lc_part_num + "-"
            ):
                cerror(
                    f"FPGA id [{fpga_id}] does not match part-num [{part_num}]"
                )
                sys.exit(1)

        # -- Load programmers definitions. Optional project custom definition
        # -- supersede apio standard definitions.
        self.programmers, self.custom_programmers_ids = self._load_definitions(
            PROGRAMMERS_JSONC,
            self._package_definitions_dir,
            self._project_definitions_dir,
        )

        # -- Validate programmers definitions.
        for programmer_id, programmer_info in self.programmers.items():
            if not ID_FORMAT.match(programmer_id):
                cerror(f"Programmer id has an invalid format: {programmer_id}")
                sys.exit(1)
            try:
                validate(instance=programmer_info, schema=PROGRAMMER_SCHEMA)
            except ValidationError as e:
                cerror(
                    f"Invalid programmer definition [{programmer_id}]: "
                    f"{e.message}"
                )
                sys.exit(1)

        # -- Check references from boards to fpga and programmers
        for board_id, board_definition in self.boards.items():
            fpga_id = board_definition.fpga_id
            if fpga_id not in self.fpgas:
                cerror(
                    f"Board '{board_id}' refers to  non existing "
                    f"fpga '{fpga_id}'"
                )
                sys.exit(1)

            programmer_id = board_definition.programmer.id
            if programmer_id not in self.programmers:
                cerror(
                    f"Board '{board_id}' refers to a non existing "
                    f"programmer '{programmer_id}'"
                )
                sys.exit(1)

    def is_custom_board(self, board_id: str) -> bool:
        """Returns true if the board's definition was loaded from a
        project's boards.jsonc file."""
        assert board_id in self.boards, board_id
        return board_id in self.custom_boards_ids

    def is_custom_fpga(self, fpga_id: str) -> bool:
        """Returns true if the fpga's definition was loaded from a
        project's fpgas.jsonc file."""
        assert fpga_id in self.fpgas, fpga_id
        return fpga_id in self.custom_fpgas_ids

    def is_custom_programmer(self, programmer_id: str) -> bool:
        """Returns true if the programmer's definition was loaded from a
        project's programmers.jsonc file."""
        assert programmer_id in self.programmers, programmer_id
        return programmer_id in self.custom_programmers_ids

    @classmethod
    def _load_definitions(
        cls,
        name: str,
        package_definitions_dir: Path,
        project_definitions_dir: Path,
    ) -> Tuple[Dict[str, Dict], Set[str]]:
        """Load a jsonc file. Try first from custom_dir, if given, and then
        from standard dir. This method is called for resource files in
        apio/resources and definitions files in the definitions packages.
        Returns a tuple with the merged standard and custom resource
        definitions (custom wins) and a set of boards ids in the custom
        resource file.
        """

        # -- Load the standard definition as a json dict.
        filepath = package_definitions_dir / name
        combined_dict = cls._load_definitions_file(filepath)
        custom_ids = set()

        # -- If there is a project specific override file, apply it on
        # -- top of the standard apio definition dict.
        if project_definitions_dir:
            filepath = project_definitions_dir / name
            if filepath.exists():
                # -- Load the override json dict.
                cout(f"Loading custom '{name}'.")
                custom_dict = cls._load_definitions_file(filepath)
                # -- Apply the override. Entries in override replace same
                # -- key entries in result or if unique are added.
                combined_dict.update(custom_dict)
                custom_ids.update(custom_dict.keys())

        # -- All done.
        return (combined_dict, custom_ids)

    @classmethod
    def _load_definitions_file(cls, filepath: Path) -> dict:
        """Load the resources from a given jsonc file path
        * OUTPUT: A dictionary with the jsonc file data
          In case of error it raises an exception and finish
        """

        # pylint: disable=broad-exception-caught

        # -- Read the jsonc file
        try:
            jsonc_text = filepath.read_text(encoding="utf-8")
            json_dict = json5.loads(jsonc_text)
        except Exception as e:
            cerror(
                f"Failed to read and parse definition file {filepath.name}",
                f"{e}",
            )
            sys.exit(1)

        # -- Return the object for the resource
        return json_dict
