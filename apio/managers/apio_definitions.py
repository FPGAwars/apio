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
from apio.common.apio_console import cout, cerror

# -- Boards definitions file name.
BOARDS_JSONC = "boards.jsonc"

# -- FPGAs definitions file name.
FPGAS_JSONC = "fpgas.jsonc"

# -- Programmers definitions file name.
PROGRAMMERS_JSONC = "programmers.jsonc"

# -- A regex for validating boards, fpgas, and programmers ids.
ID_FORMAT = re.compile(r"^[a-z][a-z0-9-]*$")


# -- JSON schema for validating a single board definition in boards.jsonc.
# -- The field 'description' is for information only.
BOARD_SCHEMA = schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["description", "fpga-id", "programmer"],
    "properties": {
        "description": {"type": "string"},
        "fpga-id": {"type": "string"},
        "programmer": {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {"type": "string"},
                "extra-args": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "usb": {
            "type": "object",
            "required": ["vid", "pid"],
            "properties": {
                "vid": {"type": "string", "pattern": "^[0-9a-f]{4}$"},
                "pid": {"type": "string", "pattern": "^[0-9a-f]{4}$"},
                "product-regex": {"type": "string", "pattern": "^.*$"},
            },
            "additionalProperties": False,
        },
        "tinyprog": {
            "type": "object",
            "required": ["name-regex"],
            "properties": {
                "name-regex": {"type": "string", "pattern": "^.*$"},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

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

    def __init__(
        self,
        package_definitions_dir: Path,
        project_definitions_dir: Optional[Path],
    ):

        assert isinstance(package_definitions_dir, Path)
        assert project_definitions_dir is None or isinstance(
            project_definitions_dir, Path
        )

        self._package_definitions_dir = package_definitions_dir
        self._project_definitions_dir = project_definitions_dir

        # -- Read boards definitions.
        self.boards, self.custom_boards_ids = self._load_definitions(
            BOARDS_JSONC,
            self._package_definitions_dir,
            self._project_definitions_dir,
        )

        # -- Validate boards definitions. Optional project custom definition
        # -- supersede apio standard definitions.
        for board_id, board_info in self.boards.items():
            if not ID_FORMAT.match(board_id):
                cerror(f"Board id has an invalid format: {board_id}")
                sys.exit(1)
            try:
                validate(instance=board_info, schema=BOARD_SCHEMA)
            except ValidationError as e:
                cerror(f"Invalid board definition [{board_id}]: {e.message}")
                sys.exit(1)

        # -- Read fpgas definitions.
        self.fpgas, self.custom_fpgas_ids = self._load_definitions(
            FPGAS_JSONC,
            self._package_definitions_dir,
            self._project_definitions_dir,
        )

        # -- Validate fpgas definitions. Optional project custom definition
        # -- supersede apio standard definitions.
        for fpga_id, fpga_info in self.fpgas.items():
            if not ID_FORMAT.match(fpga_id):
                cerror(f"FPGA id has an invalid format: {fpga_id}")
                sys.exit(1)
            try:
                validate(instance=fpga_info, schema=FPGA_SCHEMA)
            except ValidationError as e:
                cerror(f"Invalid fpga definition [{fpga_id}]: {e.message}")
                sys.exit(1)

            # -- Expecting a params field for the specified architecture.
            params_pattern = re.compile(r".*-params$")
            actual_params = [
                key for key in fpga_info if params_pattern.match(key)
            ]
            expected_params = [fpga_info["arch"] + "-params"]
            if actual_params != expected_params:
                cerror(f"Unexpected params {actual_params} in fpga {fpga_id}")
                sys.exit(1)
            part_num = fpga_info["part-num"]
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
