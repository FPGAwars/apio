
# pylint: disable=all

from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BoardProgrammer(_message.Message):
    __slots__ = ("id", "extra_args")
    ID_FIELD_NUMBER: _ClassVar[int]
    EXTRA_ARGS_FIELD_NUMBER: _ClassVar[int]
    id: str
    extra_args: str
    def __init__(self, id: _Optional[str] = ..., extra_args: _Optional[str] = ...) -> None: ...

class BoardUsb(_message.Message):
    __slots__ = ("vid", "pid", "product_regex")
    VID_FIELD_NUMBER: _ClassVar[int]
    PID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_REGEX_FIELD_NUMBER: _ClassVar[int]
    vid: str
    pid: str
    product_regex: str
    def __init__(self, vid: _Optional[str] = ..., pid: _Optional[str] = ..., product_regex: _Optional[str] = ...) -> None: ...

class BoardTinyprog(_message.Message):
    __slots__ = ("name_regex",)
    NAME_REGEX_FIELD_NUMBER: _ClassVar[int]
    name_regex: str
    def __init__(self, name_regex: _Optional[str] = ...) -> None: ...

class BoardDefinition(_message.Message):
    __slots__ = ("description", "fpga_id", "programmer", "usb", "tinyprog")
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FPGA_ID_FIELD_NUMBER: _ClassVar[int]
    PROGRAMMER_FIELD_NUMBER: _ClassVar[int]
    USB_FIELD_NUMBER: _ClassVar[int]
    TINYPROG_FIELD_NUMBER: _ClassVar[int]
    description: str
    fpga_id: str
    programmer: BoardProgrammer
    usb: BoardUsb
    tinyprog: BoardTinyprog
    def __init__(self, description: _Optional[str] = ..., fpga_id: _Optional[str] = ..., programmer: _Optional[_Union[BoardProgrammer, _Mapping]] = ..., usb: _Optional[_Union[BoardUsb, _Mapping]] = ..., tinyprog: _Optional[_Union[BoardTinyprog, _Mapping]] = ...) -> None: ...

class Definitions(_message.Message):
    __slots__ = ("boards",)
    class BoardsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: BoardDefinition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[BoardDefinition, _Mapping]] = ...) -> None: ...
    BOARDS_FIELD_NUMBER: _ClassVar[int]
    boards: _containers.MessageMap[str, BoardDefinition]
    def __init__(self, boards: _Optional[_Mapping[str, BoardDefinition]] = ...) -> None: ...
