# pylint: disable=all

from apio.common.proto import apio_common_pb2 as _apio_common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BoardProgrammerSection(_message.Message):
    __slots__ = ("id", "extra_args")
    ID_FIELD_NUMBER: _ClassVar[int]
    EXTRA_ARGS_FIELD_NUMBER: _ClassVar[int]
    id: str
    extra_args: str
    def __init__(self, id: _Optional[str] = ..., extra_args: _Optional[str] = ...) -> None: ...

class BoardUsbSection(_message.Message):
    __slots__ = ("vid", "pid", "product_regex")
    VID_FIELD_NUMBER: _ClassVar[int]
    PID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_REGEX_FIELD_NUMBER: _ClassVar[int]
    vid: str
    pid: str
    product_regex: str
    def __init__(self, vid: _Optional[str] = ..., pid: _Optional[str] = ..., product_regex: _Optional[str] = ...) -> None: ...

class BoardTinyprogSection(_message.Message):
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
    programmer: BoardProgrammerSection
    usb: BoardUsbSection
    tinyprog: BoardTinyprogSection
    def __init__(self, description: _Optional[str] = ..., fpga_id: _Optional[str] = ..., programmer: _Optional[_Union[BoardProgrammerSection, _Mapping]] = ..., usb: _Optional[_Union[BoardUsbSection, _Mapping]] = ..., tinyprog: _Optional[_Union[BoardTinyprogSection, _Mapping]] = ...) -> None: ...

class FpgaIce40Params(_message.Message):
    __slots__ = ("type", "package")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_FIELD_NUMBER: _ClassVar[int]
    type: str
    package: str
    def __init__(self, type: _Optional[str] = ..., package: _Optional[str] = ...) -> None: ...

class FpgaEcp5Params(_message.Message):
    __slots__ = ("type", "package", "speed")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    type: str
    package: str
    speed: str
    def __init__(self, type: _Optional[str] = ..., package: _Optional[str] = ..., speed: _Optional[str] = ...) -> None: ...

class FpgaGowinParams(_message.Message):
    __slots__ = ("yosys_family", "nextpnr_family", "packer_device")
    YOSYS_FAMILY_FIELD_NUMBER: _ClassVar[int]
    NEXTPNR_FAMILY_FIELD_NUMBER: _ClassVar[int]
    PACKER_DEVICE_FIELD_NUMBER: _ClassVar[int]
    yosys_family: str
    nextpnr_family: str
    packer_device: str
    def __init__(self, yosys_family: _Optional[str] = ..., nextpnr_family: _Optional[str] = ..., packer_device: _Optional[str] = ...) -> None: ...

class FpgaXilinxParams(_message.Message):
    __slots__ = ("family", "yosys_arch", "package", "speed")
    FAMILY_FIELD_NUMBER: _ClassVar[int]
    YOSYS_ARCH_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    family: str
    yosys_arch: str
    package: str
    speed: str
    def __init__(self, family: _Optional[str] = ..., yosys_arch: _Optional[str] = ..., package: _Optional[str] = ..., speed: _Optional[str] = ...) -> None: ...

class FpgaDefinition(_message.Message):
    __slots__ = ("part_num", "arch", "size", "ice40_params", "ecp5_params", "gowin_params", "xilinx_params")
    PART_NUM_FIELD_NUMBER: _ClassVar[int]
    ARCH_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    ICE40_PARAMS_FIELD_NUMBER: _ClassVar[int]
    ECP5_PARAMS_FIELD_NUMBER: _ClassVar[int]
    GOWIN_PARAMS_FIELD_NUMBER: _ClassVar[int]
    XILINX_PARAMS_FIELD_NUMBER: _ClassVar[int]
    part_num: str
    arch: _apio_common_pb2.ApioArch
    size: str
    ice40_params: FpgaIce40Params
    ecp5_params: FpgaEcp5Params
    gowin_params: FpgaGowinParams
    xilinx_params: FpgaXilinxParams
    def __init__(self, part_num: _Optional[str] = ..., arch: _Optional[_Union[_apio_common_pb2.ApioArch, str]] = ..., size: _Optional[str] = ..., ice40_params: _Optional[_Union[FpgaIce40Params, _Mapping]] = ..., ecp5_params: _Optional[_Union[FpgaEcp5Params, _Mapping]] = ..., gowin_params: _Optional[_Union[FpgaGowinParams, _Mapping]] = ..., xilinx_params: _Optional[_Union[FpgaXilinxParams, _Mapping]] = ...) -> None: ...

class ProgrammerDefinition(_message.Message):
    __slots__ = ("command", "args")
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    command: str
    args: str
    def __init__(self, command: _Optional[str] = ..., args: _Optional[str] = ...) -> None: ...
