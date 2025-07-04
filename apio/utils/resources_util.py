"""Utilities related to the Apio resource files."""

import sys
from typing import Any, Dict
from dataclasses import dataclass
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from apio.common.apio_console import cerror


@dataclass(frozen=True)
class ProjectResources:
    """Contains the resources of the current project."""

    board_id: str
    board_info: Dict[str, Any]
    fpga_id: str
    fpga_info: Dict[str, Any]
    programmer_id: str
    programmer_info: Dict[str, Any]


# -- A schema for validating the JSON board definitions in boards.jsonc.
BOARD_SCHEMA = schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["description", "fpga-id", "programmer"],
    "properties": {
        "description": {"type": "string"},
        "legacy-name": {"type": "string"},
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

FPGA_SCHEMA = schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["part-num", "arch", "size", "type"],
    "properties": {
        "part-num": {"type": "string"},
        "arch": {"type": "string"},
        "size": {"type": "string"},
        "type": {"type": "string"},
        "pack": {"type": "string"},
        "speed": {"type": "string"},
    },
    "additionalProperties": False,
}

PROGRAMMER_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["command", "args"],
    "properties": {"command": {"type": "string"}, "args": {"type": "string"}},
    "additionalProperties": False,
}


def validate_board_info(board_id: str, board_info: dict) -> None:
    """Check the given board info and raise a fatal error on any error."""
    try:
        validate(instance=board_info, schema=BOARD_SCHEMA)
    except ValidationError as e:
        cerror(f"Invalid board definition [{board_id}]: {e.message}")
        sys.exit(1)


def validate_fpga_info(fpga_id: str, fpga_info: dict) -> None:
    """Check the given fpga info and raise a fatal error on any error."""
    try:
        validate(instance=fpga_info, schema=FPGA_SCHEMA)
    except ValidationError as e:
        cerror(f"Invalid fpga definitions [{fpga_id}]: {e.message}")
        sys.exit(1)


def validate_programmer_info(
    programmer_id: str, programmer_info: dict
) -> None:
    """Check the given programmer info and raise a fatal error on any error."""
    try:
        validate(instance=programmer_info, schema=PROGRAMMER_SCHEMA)
    except ValidationError as e:
        cerror(f"Invalid programmer definition [{programmer_id}]: {e.message}")
        sys.exit(1)


def validate_project_resources(res: ProjectResources) -> None:
    """Check the resources of the current project. Exit with an error
    message on any error."""
    validate_board_info(res.board_id, res.board_info)
    validate_fpga_info(res.fpga_id, res.fpga_info)
    validate_programmer_info(res.programmer_id, res.programmer_info)

    # TODO: Add here additional check.
