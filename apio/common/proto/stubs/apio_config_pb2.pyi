# *** Apio patched line:
# pylint: disable=all

from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApioPackageSpec(_message.Message):
    __slots__ = ("description",)
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    description: str
    def __init__(self, description: _Optional[str] = ...) -> None: ...

class ApioPlatformEnvSpec(_message.Message):
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

class ApioPlatformSpec(_message.Message):
    __slots__ = ("packages", "env")
    PACKAGES_FIELD_NUMBER: _ClassVar[int]
    ENV_FIELD_NUMBER: _ClassVar[int]
    packages: _containers.RepeatedScalarFieldContainer[str]
    env: ApioPlatformEnvSpec
    def __init__(self, packages: _Optional[_Iterable[str]] = ..., env: _Optional[_Union[ApioPlatformEnvSpec, _Mapping]] = ...) -> None: ...

class ApioRemoteConfigSpec(_message.Message):
    __slots__ = ("ttl_days", "retry_minutes", "url")
    TTL_DAYS_FIELD_NUMBER: _ClassVar[int]
    RETRY_MINUTES_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    ttl_days: int
    retry_minutes: int
    url: str
    def __init__(self, ttl_days: _Optional[int] = ..., retry_minutes: _Optional[int] = ..., url: _Optional[str] = ...) -> None: ...

class ApioRawConfig(_message.Message):
    __slots__ = ("packages", "platforms", "remote_config")
    class PackagesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ApioPackageSpec
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ApioPackageSpec, _Mapping]] = ...) -> None: ...
    class PlatformsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ApioPlatformSpec
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ApioPlatformSpec, _Mapping]] = ...) -> None: ...
    PACKAGES_FIELD_NUMBER: _ClassVar[int]
    PLATFORMS_FIELD_NUMBER: _ClassVar[int]
    REMOTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    packages: _containers.MessageMap[str, ApioPackageSpec]
    platforms: _containers.MessageMap[str, ApioPlatformSpec]
    remote_config: ApioRemoteConfigSpec
    def __init__(self, packages: _Optional[_Mapping[str, ApioPackageSpec]] = ..., platforms: _Optional[_Mapping[str, ApioPlatformSpec]] = ..., remote_config: _Optional[_Union[ApioRemoteConfigSpec, _Mapping]] = ...) -> None: ...
