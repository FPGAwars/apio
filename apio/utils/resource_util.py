"""Utilities related to the Apio resource files."""

from dataclasses import dataclass
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from apio.common.apio_console import fatal_error
from apio.common import proto_util
from apio.managers.apio_definitions import ApioDefinitions
from apio.common.proto.apio_definitions_pb2 import (
    BoardDefinition,
    FpgaDefinition,
    ProgrammerDefinition,
)


@dataclass(frozen=True)
class ProjectResources:
    """Contains the resources of the current project."""

    board_id: str
    board_definition: BoardDefinition
    fpga_id: str
    fpga_definition: FpgaDefinition
    programmer_id: str
    programmer_definition: ProgrammerDefinition


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
                        "add-to-path": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "delete-env-vars": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "add-env-vars": {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                        },
                        "define-consts": {
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


def validate_config(config: dict) -> None:
    """Check the config resource from config.jsonc."""
    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
    except ValidationError as e:
        fatal_error("Invalid config.", cause=e)


def validate_packages(packages: dict) -> None:
    """Check the packages resource from packages.jsonc."""
    try:
        validate(instance=packages, schema=PACKAGES_SCHEMA)
    except ValidationError as e:
        fatal_error("Invalid packages resource.", cause=e)


def collect_project_resources(
    board_id: str,
    definitions: ApioDefinitions,
) -> ProjectResources:
    """Collect and validate the resources used by a project. Since the
    resources may be custom resources defined by the user, we need to
    have a user friendly error handling and reporting."""

    # -- Get the board definition.
    board_definition = definitions.boards.get(board_id, None)
    if board_definition is None:
        fatal_error(f"Unknown board id '{board_id}'.")

    # -- We assume below that these fields are required.
    proto_util.check_is_required(board_definition, "fpga_id", "programmer.id")

    # -- Get fpga id and definition.
    fpga_id = board_definition.fpga_id
    fpga_definition = definitions.fpgas[fpga_id]

    # -- Get programmer id and info.
    programmer_id = board_definition.programmer.id
    programmer_definition = definitions.programmers[programmer_id]

    # -- Create the project resources bundle.
    project_resources = ProjectResources(
        board_id,
        board_definition,
        fpga_id,
        fpga_definition,
        programmer_id,
        programmer_definition,
    )

    # -- All done
    return project_resources
