# *** Apio patched line:
# pylint: disable=all

# *** Apio patched line:
from . import apio_common_pb2 as _apio_common_pb2
# *** Apio patched line:
from . import apio_definitions_pb2 as _apio_definitions_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApioPartEntry(_message.Message):
    __slots__ = ("generated", "definition")
    GENERATED_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_FIELD_NUMBER: _ClassVar[int]
    generated: bool
    definition: _apio_definitions_pb2.FpgaDefinition
    def __init__(self, generated: bool = ..., definition: _Optional[_Union[_apio_definitions_pb2.FpgaDefinition, _Mapping]] = ...) -> None: ...
