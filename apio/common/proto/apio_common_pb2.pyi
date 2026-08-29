# pylint: disable=all

from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ApioArch(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ARCH_UNSPECIFIED: _ClassVar[ApioArch]
    ICE40: _ClassVar[ApioArch]
    ECP5: _ClassVar[ApioArch]
    GOWIN: _ClassVar[ApioArch]
    XILINX: _ClassVar[ApioArch]
ARCH_UNSPECIFIED: ApioArch
ICE40: ApioArch
ECP5: ApioArch
GOWIN: ApioArch
XILINX: ApioArch
