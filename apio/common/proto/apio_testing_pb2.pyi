# pylint: disable=all

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MessageA(_message.Message):
    __slots__ = ("field_a1", "field_a2")
    FIELD_A1_FIELD_NUMBER: _ClassVar[int]
    FIELD_A2_FIELD_NUMBER: _ClassVar[int]
    field_a1: str
    field_a2: str
    def __init__(self, field_a1: _Optional[str] = ..., field_a2: _Optional[str] = ...) -> None: ...

class MessageB(_message.Message):
    __slots__ = ("field_b1", "field_b2")
    FIELD_B1_FIELD_NUMBER: _ClassVar[int]
    FIELD_B2_FIELD_NUMBER: _ClassVar[int]
    field_b1: MessageA
    field_b2: MessageA
    def __init__(self, field_b1: _Optional[_Union[MessageA, _Mapping]] = ..., field_b2: _Optional[_Union[MessageA, _Mapping]] = ...) -> None: ...
