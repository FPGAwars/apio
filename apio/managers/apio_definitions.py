"""The apio definitions manager class. This class manages the standard
and custom boards, fpgas, and programmers definitions."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2


import re
from pathlib import Path
from typing import Dict, Set, Tuple, Optional
import json5
from apio.common import proto_util
from apio.common.apio_console import cout, fatal_error
from apio.common.proto.apio_definitions_pb2 import (
    BoardDefinition,
    FpgaDefinition,
    ProgrammerDefinition,
)

# -- Boards definitions file name.
BOARDS_JSONC = "boards.jsonc"

# -- FPGAs definitions file name.
FPGAS_JSONC = "fpgas.jsonc"

# -- Programmers definitions file name.
PROGRAMMERS_JSONC = "programmers.jsonc"

# -- A regex for validating boards, fpgas, and programmers ids.
DEFINITION_ID_FORMAT = re.compile(r"^[a-z][a-z0-9-]*$")

# -- A regex for validating usb vid and pid values.
USB_ID_FORMAT = re.compile(r"^[0-9a-f]{4}$")


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

        # -- Read boards definitions as json_dicts.
        # -- Custom definitions overrides apio standard definitions.
        boards_json, self.custom_boards_ids = self._load_definitions(
            BOARDS_JSONC,
            self._package_definitions_dir,
            self._project_definitions_dir,
        )

        # -- Convert the board definition to BoardDefinition protos and save.
        self.boards: Dict[str, BoardDefinition] = {}
        for board_id, definition_dict in boards_json.items():
            definition = proto_util.proto_from_json_dict(
                definition_dict,
                BoardDefinition,
                f"Failed to parse board definition '{board_id}",
            )
            self.boards[board_id] = definition

        # -- Read fpgas definitions as json dicts.
        # -- Custom definitions overrides apio standard definitions.
        fpgas_json, self.custom_fpgas_ids = self._load_definitions(
            FPGAS_JSONC,
            self._package_definitions_dir,
            self._project_definitions_dir,
        )

        # -- Convert the fpgas definition dicts to FpgasDefinition protos and
        # -- save.
        self.fpgas: Dict[str, FpgaDefinition] = {}
        for fpga_id, definition_dict in fpgas_json.items():
            definition = proto_util.proto_from_json_dict(
                definition_dict,
                FpgaDefinition,
                f"Failed to parse fpga definition '{fpga_id}",
            )
            self.fpgas[fpga_id] = definition

        # -- Load programmers definitions as json dicts.
        # -- Custom definitions overrides apio standard definitions.
        programmers_json, self.custom_programmers_ids = self._load_definitions(
            PROGRAMMERS_JSONC,
            self._package_definitions_dir,
            self._project_definitions_dir,
        )

        # -- Convert the programmers definition dicts to FpgaDefinition protos
        # -- and save.
        self.programmers: Dict[str, ProgrammerDefinition] = {}
        for programmer_id, definition_dict in programmers_json.items():
            definition = proto_util.proto_from_json_dict(
                definition_dict,
                ProgrammerDefinition,
                f"Failed to parse programmer definition '{programmer_id}",
            )
            self.programmers[programmer_id] = definition

        # -- Validate the definitions we just loaded.
        self._validate_definitions()

    def _validate_definitions(self):
        """Validate the boards, fpgas, and programmers definitions of this
        instance."""

        # pylint: disable=too-many-branches

        # -- Validate boards definitions
        for board_id, board_definition in self.boards.items():
            # -- Check that board id has a valid format.
            if not DEFINITION_ID_FORMAT.match(board_id):
                fatal_error(f"Board id `{board_id}` has an invalid format")

            # -- Check that the definition proto is fully initialized.
            proto_util.check_is_initialized(
                board_definition,
                f"Failed to initialized board definition '{board_id}'",
            )

            # -- Check that the fpga definition exits.
            proto_util.check_is_required(board_definition, "fpga_id")
            fpga_id = board_definition.fpga_id
            if fpga_id not in self.fpgas:
                fatal_error(
                    f"Board `{board_id}` refers to non existing "
                    + f"fpga `{fpga_id}`"
                )

            # -- Check that the programmer definition exits.
            proto_util.check_is_required(board_definition, "programmer.id")
            programmer_id = board_definition.programmer.id
            if programmer_id not in self.programmers:
                fatal_error(
                    f"Board `{board_id}` refers to non existing "
                    + f"programmer `{programmer_id}`"
                )

            # -- Validate the format of the optional usb.vid and usb.pid
            # -- fields.
            proto_util.check_not_required(board_definition, "usb")
            if board_definition.HasField("usb"):
                usb = board_definition.usb
                # -- Check vid
                proto_util.check_not_required(usb, "vid")
                if usb.HasField("vid"):
                    if not USB_ID_FORMAT.match(usb.vid):
                        fatal_error(
                            "The usb.vid field of the board "
                            + f"'{board_id}' has invalid value `{usb.vid}`"
                        )
                # -- check pid
                proto_util.check_not_required(usb, "pid")
                if usb.HasField("pid"):
                    if not USB_ID_FORMAT.match(usb.pid):
                        fatal_error(
                            "The usb.pid field of the board "
                            + f"'{board_id}' has invalid value `{usb.vip}`"
                        )

        # -- Validate fpgas definitions.
        for fpga_id, fpga_definition in self.fpgas.items():
            # -- Check id format.
            if not DEFINITION_ID_FORMAT.match(fpga_id):
                fatal_error(f"FPGA id has an invalid format: {fpga_id}")

            # -- Check that the definition proto is fully initialized.
            proto_util.check_is_initialized(
                fpga_definition,
                f"Failed to initialize fpga definition '{fpga_id}'",
            )

        # -- Validate programmers definitions.
        for programmer_id, programmer_definition in self.programmers.items():
            # -- Check id format.
            if not DEFINITION_ID_FORMAT.match(programmer_id):
                fatal_error(
                    f"Programmer id has an invalid format: {programmer_id}"
                )

            # -- Check that the definition proto is fully initialized.
            proto_util.check_is_initialized(
                programmer_definition,
                f"Failed to initialize programmer definition '{fpga_id}'",
            )

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
            fatal_error(
                f"Failed to read and parse definition file {filepath.name}",
                cause=e,
            )

        # -- Return the object for the resource
        return json_dict
