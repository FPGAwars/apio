"""Utilities related to the Apio Protocol Buffers objects."""

import sys
import re
from typing import Any, Dict, TypeVar
from google.protobuf.json_format import ParseDict
from google.protobuf.message import Message
from google.protobuf.unknown_fields import UnknownFieldSet
from google.protobuf.json_format import MessageToDict
from apio.common.apio_console import cerror


# Placeholder for a concrete protobuf message *class* (e.g. MyProto),
# not an instance. bound=Message restricts it to subclasses of
# google.protobuf.message.Message. A TypeVar (vs plain type[Message])
# lets the type checker keep the specific class: pass MyProto, get MyProto.
MessageClass = TypeVar("MessageClass", bound=Message)


# TODO: Move to a util module.
def check_proto_is_initialized(
    msg: Message, error_context: str, *, json_naming: bool = False
) -> None:
    """Check that a proto message is fully populated"""

    # -- Check 1: All required fields should present.
    if not msg.IsInitialized():
        # -- Report the first missing required field.
        missing_field: str = msg.FindInitializationErrors()[0]
        if json_naming:
            missing_field = missing_field.replace("_", "-")
        cerror(error_context, f"Missing required field '{missing_field}'")
        sys.exit(1)

    # -- Check 2: Should not carry unknown fields.
    unknown_fields = list(UnknownFieldSet(msg))
    if len(unknown_fields) > 0:
        cerror(error_context, f'Unknown fields: {", ".join(unknown_fields)}')
        sys.exit(1)


def proto_from_json_dict(
    json_dict: Dict[str, Any],
    proto_class: type[MessageClass],
    error_context: str,
) -> MessageClass:
    """Create and return an object of proto message class 'proto_class'
    populated with values from json dict json_dict. Exit with an error code
    on any error.
    """
    # pylint: disable=broad-exception-caught

    try:
        proto_msg = ParseDict(json_dict, proto_class())
    except Exception as e:
        error_msg = str(e)

        # -- Try to improve the error message.
        pattern = re.compile(r'has no field named "([^"]+)" at')
        match = pattern.search(error_msg)
        if match:
            error_msg = f"Unknown field '{match.group(1)}'"

        cerror(error_context, error_msg)
        sys.exit(1)

    check_proto_is_initialized(proto_msg, error_context, json_naming=True)
    return proto_msg


def proto_to_json_dict(proto_msg: Message) -> Dict[str, Any]:
    """Given a proto object, convert it to a json dict."""
    return MessageToDict(proto_msg)
