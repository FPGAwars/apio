# pylint: disable=all

from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RemoteConfigRepositorySpec(_message.Message):
    __slots__ = ("name", "organization")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    name: str
    organization: str
    def __init__(self, name: _Optional[str] = ..., organization: _Optional[str] = ...) -> None: ...

class RemoteConfigReleaseSpec(_message.Message):
    __slots__ = ("tag", "package")
    TAG_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_FIELD_NUMBER: _ClassVar[int]
    tag: str
    package: str
    def __init__(self, tag: _Optional[str] = ..., package: _Optional[str] = ...) -> None: ...

class RemoteConfigPackageSpec(_message.Message):
    __slots__ = ("repository", "release")
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    RELEASE_FIELD_NUMBER: _ClassVar[int]
    repository: RemoteConfigRepositorySpec
    release: RemoteConfigReleaseSpec
    def __init__(self, repository: _Optional[_Union[RemoteConfigRepositorySpec, _Mapping]] = ..., release: _Optional[_Union[RemoteConfigReleaseSpec, _Mapping]] = ...) -> None: ...

class RemoteConfigSpec(_message.Message):
    __slots__ = ("packages",)
    class PackagesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: RemoteConfigPackageSpec
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[RemoteConfigPackageSpec, _Mapping]] = ...) -> None: ...
    PACKAGES_FIELD_NUMBER: _ClassVar[int]
    packages: _containers.MessageMap[str, RemoteConfigPackageSpec]
    def __init__(self, packages: _Optional[_Mapping[str, RemoteConfigPackageSpec]] = ...) -> None: ...

class CachedRemoteConfigMetadata(_message.Message):
    __slots__ = ("loaded_by", "loaded_at", "loaded_from", "refresh_failure_on")
    LOADED_BY_FIELD_NUMBER: _ClassVar[int]
    LOADED_AT_FIELD_NUMBER: _ClassVar[int]
    LOADED_FROM_FIELD_NUMBER: _ClassVar[int]
    REFRESH_FAILURE_ON_FIELD_NUMBER: _ClassVar[int]
    loaded_by: str
    loaded_at: str
    loaded_from: str
    refresh_failure_on: str
    def __init__(self, loaded_by: _Optional[str] = ..., loaded_at: _Optional[str] = ..., loaded_from: _Optional[str] = ..., refresh_failure_on: _Optional[str] = ...) -> None: ...

class CachedRemoteConfigSpec(_message.Message):
    __slots__ = ("remote_config", "metadata")
    REMOTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    remote_config: RemoteConfigSpec
    metadata: CachedRemoteConfigMetadata
    def __init__(self, remote_config: _Optional[_Union[RemoteConfigSpec, _Mapping]] = ..., metadata: _Optional[_Union[CachedRemoteConfigMetadata, _Mapping]] = ...) -> None: ...
