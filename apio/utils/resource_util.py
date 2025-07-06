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


# -- JSON schema for validating board definitions in boards.jsonc.
# -- The field 'description' is for information only.
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

# -- JSON schema for validating fpga definitions in fpga.jsonc.
# -- The fields 'part-num' and 'size' are for information only.
FPGA_SCHEMA = schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["part-num", "arch", "size", "type"],
    "properties": {
        "part-num": {"type": "string"},
        "arch": {"type": "string", "enum": ["ice40", "ecp5", "gowin"]},
        "size": {"type": "string"},
        "type": {"type": "string"},
        "pack": {"type": "string"},
        "speed": {"type": "string"},
    },
    "additionalProperties": False,
}

# -- JSON schema for validating programmer definitions in programmers.jsonc.
PROGRAMMER_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["command", "args"],
    "properties": {"command": {"type": "string"}, "args": {"type": "string"}},
    "additionalProperties": False,
}

# -- JSON schema for validating config.jsonc.
CONFIG_SCHEMA = {
    "type": "object",
    "required": [
        "remote-config-ttl-days",
        "remote-config-retry-minutes",
        "remote-config-url",
    ],
    "properties": {
        "remote-config-ttl-days": {"type": "integer", "minimum": 1},
        "remote-config-retry-minutes": {"type": "integer", "minimum": 0},
        "remote-config-url": {"type": "string"},
    },
    "additionalProperties": False,
}

# -- JSON schema for validating platforms.jsonc.
PLATFORMS_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^[a-z]+(-[a-z0-9]+)+$": {  # matches keys like "darwin-arm64"
            "type": "object",
            "required": ["type", "variant"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["Mac OSX", "Linux", "Windows"],
                },
                "variant": {"type": "string"},
            },
            "additionalProperties": False,
        }
    },
    "additionalProperties": False,
}

# -- JSON schema for validating packages.jsonc.
PACKAGES_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^[a-z0-9_-]+$": {  # package names like "oss-cad-suite"
            "type": "object",
            "required": ["description", "env"],
            "properties": {
                "description": {"type": "string"},
                "restricted-to-platforms": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "env": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "array", "items": {"type": "string"}},
                        "vars": {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        }
    },
    "additionalProperties": False,
}


def _validate_board_info(board_id: str, board_info: dict) -> None:
    """Check the given board info and raise a fatal error on any error."""
    try:
        validate(instance=board_info, schema=BOARD_SCHEMA)
    except ValidationError as e:
        cerror(f"Invalid board definition [{board_id}]: {e.message}")
        sys.exit(1)


def _validate_fpga_info(fpga_id: str, fpga_info: dict) -> None:
    """Check the given fpga info and raise a fatal error on any error."""
    try:
        validate(instance=fpga_info, schema=FPGA_SCHEMA)
    except ValidationError as e:
        cerror(f"Invalid fpga definitions [{fpga_id}]: {e.message}")
        sys.exit(1)

    # -- Architecture based validation. See scons.py for the architecture
    # -- dependent use of the fields.
    arch = fpga_info["arch"]
    match arch:
        # -- Special validation for ice40.
        case "ice40":
            if "pack" not in fpga_info:
                cerror(f"Field 'pack' is missing in ice40 fpga '{fpga_id}'")
                sys.exit(1)

        # -- Special validation for ecp5
        case "ecp5":
            if "pack" not in fpga_info:
                cerror(f"Field 'pack' is missing in ecp5 fpga '{fpga_id}'")
                sys.exit(1)
            if "speed" not in fpga_info:
                cerror(f"Field 'pack' is missing in ecp5 fpga '{fpga_id}'")
                sys.exit(1)

        # -- Special validation for gowin.
        case "gowin":
            pass

        # -- Unknown arch. Should not happen since the schema validates the
        # -- arch field.
        case _:
            raise ValidationError(f"Unknown arch '{arch}' in fpga '{fpga_id}'")


def _validate_programmer_info(
    programmer_id: str, programmer_info: dict
) -> None:
    """Check the given programmer info and raise a fatal error on any error."""
    try:
        validate(instance=programmer_info, schema=PROGRAMMER_SCHEMA)
    except ValidationError as e:
        cerror(f"Invalid programmer definition [{programmer_id}]: {e.message}")
        sys.exit(1)


def validate_config(config: dict) -> None:
    """Check the config resource from config.jsonc."""
    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
    except ValidationError as e:
        cerror(f"Invalid config: {e.message}")
        sys.exit(1)


def validate_platforms(platforms: dict) -> None:
    """Check the platforms resource from platforms.jsonc."""
    try:
        validate(instance=platforms, schema=PLATFORMS_SCHEMA)
    except ValidationError as e:
        cerror(f"Invalid platforms resource: {e.message}")
        sys.exit(1)


def validate_packages(packages: dict) -> None:
    """Check the packages resource from platforms.jsonc."""
    try:
        validate(instance=packages, schema=PACKAGES_SCHEMA)
    except ValidationError as e:
        cerror(f"Invalid packages resource: {e.message}")
        sys.exit(1)


def validate_project_resources(res: ProjectResources) -> None:
    """Check the resources of the current project. Exit with an error
    message on any error."""
    _validate_board_info(res.board_id, res.board_info)
    _validate_fpga_info(res.fpga_id, res.fpga_info)
    _validate_programmer_info(res.programmer_id, res.programmer_info)

    # TODO: Add here additional check.


def collect_project_resources(
    board_id: str, boards: dict, fpgas: dict, programmers: dict
) -> ProjectResources:
    """Collect and validate the resources used by a project. Since the
    resources may be custom resources defined by the user, we need to
    have a user friendly error handling and reporting."""

    # -- Get the info.
    board_info = boards.get(board_id, None)
    if board_info is None:
        cerror(f"Unknown board id '{board_id}'.")
        sys.exit(1)

    # -- Get fpga id and info.
    fpga_id = board_info.get("fpga-id", None)
    if fpga_id is None:
        cerror(f"Board '{board_id}' has no 'fpga-id' field.")
        sys.exit(1)
    fpga_info = fpgas.get(fpga_id, None)
    if fpga_info is None:
        cerror(f"Unknown fpga id '{fpga_id}'.")
        sys.exit(1)

    # -- Get programmer id and info.
    programmer_id = board_info.get("programmer", {}).get("id", None)
    if programmer_id is None:
        cerror(f"Board '{board_id}' has no 'programmer.id'.")
        sys.exit(1)
    programmer_info = programmers.get(programmer_id, None)
    if programmer_info is None:
        cerror(f"Unknown programmer id '{programmer_id}'.")
        sys.exit(1)

    # -- Create the project resources bundle.
    project_resources = ProjectResources(
        board_id,
        board_info,
        fpga_id,
        fpga_info,
        programmer_id,
        programmer_info,
    )

    # -- All done
    return project_resources
