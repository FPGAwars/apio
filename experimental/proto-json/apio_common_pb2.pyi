
# pylint: disable=all

from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ApioArch(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    arch_unspecified: _ClassVar[ApioArch]
    ice40: _ClassVar[ApioArch]
    ecp5: _ClassVar[ApioArch]
    gowin: _ClassVar[ApioArch]
    xilinx: _ClassVar[ApioArch]
arch_unspecified: ApioArch
ice40: ApioArch
ecp5: ApioArch
gowin: ApioArch
xilinx: ApioArch
