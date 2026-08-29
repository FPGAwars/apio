"""A manager class for  to dispatch the Apio SCONS targets."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

# -- TODO: Make sure we don't carry unknown json fields.

import sys
from typing import Dict
from pathlib import Path
import json5
import json
from google.protobuf import text_format
from google.protobuf.message import Message
from google.protobuf.unknown_fields import UnknownFieldSet
from apio_definitions_pb2 import (
    BoardDefinition,
    FpgaDefinition,
    ProgrammerDefinition,
    Definitions,
)
from google.protobuf import text_format
from google.protobuf.json_format import ParseDict

from google.protobuf.json_format import MessageToJson, MessageToDict


def check_proto(msg: Message, context: str):
    """Check that a proto message is fully populated"""

    # -- Check 1: All required fields should present.
    if not msg.IsInitialized():
        # -- Report the first missing required field.
        missing_field = msg.FindInitializationErrors()[0]
        print(context)
        print(f"Missing required field {missing_field}")
        sys.exit(1)

    # -- Check 2: Should not carry unknown fields.
    unknown_fields = list(UnknownFieldSet(msg))
    if len(unknown_fields):
        print(context)
        print(f'Unknown fields: {", ".join(unknown_fields)}')
        sys.exit(1)


def read_boards_definitions(file_path: Path) -> Dict[str, BoardDefinition]:
    """Read boards.jsonc."""
    json_text = file_path.read_text(encoding="utf-8")
    json_dict = json5.loads(json_text)

    result: Dict[str, BoardDefinition] = {}
    for id, definition_dict in json_dict.items():
        definition = ParseDict(definition_dict, BoardDefinition())
        check_proto(definition, f"Error parsing board definition '{id}'")
        assert definition.IsInitialized()
        assert not UnknownFieldSet(definition)
        result[id] = definition

    return result


def read_fpgas_definitions(file_path: Path) -> Dict[str, FpgaDefinition]:
    """Read fpgas.jsonc."""
    json_text = file_path.read_text(encoding="utf-8")
    json_dict = json5.loads(json_text)

    result: Dict[str, FpgaDefinition] = {}
    for id, definition_dict in json_dict.items():
        definition = ParseDict(definition_dict, FpgaDefinition())
        check_proto(definition, f"Error parsing fpga definition '{id}'")
        assert definition.IsInitialized()
        assert not UnknownFieldSet(definition)
        result[id] = definition

    return result


def read_programmers_definitions(
    file_path: Path,
) -> Dict[str, ProgrammerDefinition]:
    """Read programmers.jsonc."""
    json_text = file_path.read_text(encoding="utf-8")
    json_dict = json5.loads(json_text)

    result: Dict[str, ProgrammerDefinition] = {}
    for id, definition_dict in json_dict.items():
        definition = ParseDict(definition_dict, ProgrammerDefinition())
        check_proto(definition, f"Error parsing programmer definition '{id}'")
        assert definition.IsInitialized()
        assert not UnknownFieldSet(definition)
        result[id] = definition

    return result


def main():
    """Main."""

    definitions_dir = Path.home() / ".apio/packages/definitions"

    boards: Dict[str, BoardDefinition] = read_boards_definitions(
        definitions_dir / "boards.jsonc"
    )

    fpgas: Dict[str, FpgaDefinition] = read_fpgas_definitions(
        definitions_dir / "fpgas.jsonc"
    )

    programmers: Dict[str, ProgrammerDefinition] = (
        read_programmers_definitions(definitions_dir / "programmers.jsonc")
    )

    definitions = Definitions(
        boards=boards,
        fpgas=fpgas,
        programmers=programmers,
    )
    assert definitions.IsInitialized()

    # boards_json = MessageToDict(definitions)["boards"]
    # print(json.dumps(boards_json, indent=2))

    definitions_json = MessageToDict(definitions)
    print(json.dumps(definitions_json, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
