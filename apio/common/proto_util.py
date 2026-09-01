"""Utilities related to the Apio Protocol Buffers objects."""

import re
from typing import Any, Dict, TypeVar
from google.protobuf.json_format import ParseDict
from google.protobuf.message import Message
from google.protobuf.unknown_fields import UnknownFieldSet
from google.protobuf.json_format import MessageToDict
from apio.common.apio_console import fatal_error

# Placeholder for a concrete protobuf message *class* (e.g. MyProto),
# not an instance. bound=Message restricts it to subclasses of
# google.protobuf.message.Message. A TypeVar (vs plain type[Message])
# lets the type checker keep the specific class: pass MyProto, get MyProto.
MessageClass = TypeVar("MessageClass", bound=Message)


def check_is_initialized(
    proto_msg: Message, error_context: str, *, json_naming: bool = False
) -> None:
    """Check that a proto message is fully populated"""

    assert isinstance(proto_msg, Message), type(proto_msg)

    # -- Check 1: All required fields should present.
    if not proto_msg.IsInitialized():
        # -- Report the first missing required field.
        missing_field: str = proto_msg.FindInitializationErrors()[0]
        if json_naming:
            missing_field = missing_field.replace("_", "-")
        fatal_error(error_context, f"Missing required field '{missing_field}'")

    # -- Check 2: Should not carry unknown fields.
    unknown_fields = list(UnknownFieldSet(proto_msg))
    if len(unknown_fields) > 0:
        fatal_error(
            error_context, f'Unknown fields: {", ".join(unknown_fields)}'
        )


def check_is_required(proto_msg: Message, *fields_names: str) -> None:
    """Check that all the names are of required fields of the proto
    object proto_msg.  Names may be nested, e.g. "field1.field2".
    """
    assert isinstance(proto_msg, Message), type(proto_msg)

    for name in fields_names:
        descriptor = proto_msg.DESCRIPTOR
        for segment in name.split("."):
            field = descriptor.fields_by_name.get(segment)
            if field is None:
                fatal_error(
                    f"Field '{name}' is not a field of "
                    "protocol buffer message "
                    f"'{proto_msg.DESCRIPTOR.full_name}'"
                )
            if not field.is_required:
                fatal_error(
                    f"Field '{name}' of '{proto_msg.DESCRIPTOR.full_name}' "
                    f"is not required"
                )
            descriptor = field.message_type


def check_not_required(proto_msg: Message, *fields_names: str) -> None:
    """Check that none of the names is a not fully required path of proto_msg.
    Names may be nested, e.g. "field1.field2". A path is not required if
    any segment along it is not required. So if "b" is optional, "a.b.c"
    is not required. Repeated fields are not required since they can have
    zero members.
    """
    assert isinstance(proto_msg, Message), type(proto_msg)

    for name in fields_names:
        descriptor = proto_msg.DESCRIPTOR
        all_required = True
        for segment in name.split("."):
            if descriptor is None:
                fatal_error(
                    f"Field '{name}' is not a field of "
                    "protocol buffer message "
                    f"'{proto_msg.DESCRIPTOR.full_name}'"
                )
            field = descriptor.fields_by_name.get(segment)
            if field is None:
                fatal_error(
                    f"Field '{name}' is not a field of "
                    "protocol buffer message "
                    f"'{proto_msg.DESCRIPTOR.full_name}'"
                )
            if not field.is_required:
                all_required = False
            descriptor = field.message_type
        if all_required:
            fatal_error(
                f"Field '{name}' of '{proto_msg.DESCRIPTOR.full_name}' "
                f"is required"
            )


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
        fatal_error(error_context, error_msg)

    check_is_initialized(proto_msg, error_context, json_naming=True)
    return proto_msg


def proto_to_json_dict(proto_msg: Message) -> Dict[str, Any]:
    """Given a proto object, convert it to a json dict."""
    assert isinstance(proto_msg, Message), type(proto_msg)
    return MessageToDict(proto_msg)
