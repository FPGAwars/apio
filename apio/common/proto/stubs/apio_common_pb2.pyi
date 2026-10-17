# *** Apio patched line:
# pylint: disable=all

from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApioArch(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ice40: _ClassVar[ApioArch]
    ecp5: _ClassVar[ApioArch]
    gowin: _ClassVar[ApioArch]
    xilinx: _ClassVar[ApioArch]
ice40: ApioArch
ecp5: ApioArch
gowin: ApioArch
xilinx: ApioArch

class NameValue(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class EnvMutations(_message.Message):
    __slots__ = ("add_to_path", "delete_env_var", "add_env_vars", "pyinstaller_linux_fix")
    ADD_TO_PATH_FIELD_NUMBER: _ClassVar[int]
    DELETE_ENV_VAR_FIELD_NUMBER: _ClassVar[int]
    ADD_ENV_VARS_FIELD_NUMBER: _ClassVar[int]
    PYINSTALLER_LINUX_FIX_FIELD_NUMBER: _ClassVar[int]
    add_to_path: _containers.RepeatedScalarFieldContainer[str]
    delete_env_var: _containers.RepeatedScalarFieldContainer[str]
    add_env_vars: _containers.RepeatedCompositeFieldContainer[NameValue]
    pyinstaller_linux_fix: bool
    def __init__(self, add_to_path: _Optional[_Iterable[str]] = ..., delete_env_var: _Optional[_Iterable[str]] = ..., add_env_vars: _Optional[_Iterable[_Union[NameValue, _Mapping]]] = ..., pyinstaller_linux_fix: bool = ...) -> None: ...
