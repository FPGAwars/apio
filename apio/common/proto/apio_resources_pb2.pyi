# pylint: disable=all

from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApioConfig(_message.Message):
    __slots__ = ("remote_config_ttl_days", "remote_config_retry_minutes", "remote_config_url")
    REMOTE_CONFIG_TTL_DAYS_FIELD_NUMBER: _ClassVar[int]
    REMOTE_CONFIG_RETRY_MINUTES_FIELD_NUMBER: _ClassVar[int]
    REMOTE_CONFIG_URL_FIELD_NUMBER: _ClassVar[int]
    remote_config_ttl_days: int
    remote_config_retry_minutes: int
    remote_config_url: str
    def __init__(self, remote_config_ttl_days: _Optional[int] = ..., remote_config_retry_minutes: _Optional[int] = ..., remote_config_url: _Optional[str] = ...) -> None: ...

class ApioPackageEnvSpec(_message.Message):
    __slots__ = ("add_to_path", "delete_env_vars", "add_env_vars", "define_consts")
    class AddEnvVarsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class DefineConstsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ADD_TO_PATH_FIELD_NUMBER: _ClassVar[int]
    DELETE_ENV_VARS_FIELD_NUMBER: _ClassVar[int]
    ADD_ENV_VARS_FIELD_NUMBER: _ClassVar[int]
    DEFINE_CONSTS_FIELD_NUMBER: _ClassVar[int]
    add_to_path: _containers.RepeatedScalarFieldContainer[str]
    delete_env_vars: _containers.RepeatedScalarFieldContainer[str]
    add_env_vars: _containers.ScalarMap[str, str]
    define_consts: _containers.ScalarMap[str, str]
    def __init__(self, add_to_path: _Optional[_Iterable[str]] = ..., delete_env_vars: _Optional[_Iterable[str]] = ..., add_env_vars: _Optional[_Mapping[str, str]] = ..., define_consts: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ApioPackageSpec(_message.Message):
    __slots__ = ("description", "restricted_to_platforms", "env")
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    RESTRICTED_TO_PLATFORMS_FIELD_NUMBER: _ClassVar[int]
    ENV_FIELD_NUMBER: _ClassVar[int]
    description: str
    restricted_to_platforms: _containers.RepeatedScalarFieldContainer[str]
    env: ApioPackageEnvSpec
    def __init__(self, description: _Optional[str] = ..., restricted_to_platforms: _Optional[_Iterable[str]] = ..., env: _Optional[_Union[ApioPackageEnvSpec, _Mapping]] = ...) -> None: ...
