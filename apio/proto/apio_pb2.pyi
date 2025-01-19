from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApioArch(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[ApioArch]
    ICE40: _ClassVar[ApioArch]
    ECP5: _ClassVar[ApioArch]
    GOWIN: _ClassVar[ApioArch]
UNSPECIFIED: ApioArch
ICE40: ApioArch
ECP5: ApioArch
GOWIN: ApioArch

class Ice40FpgaInfo(_message.Message):
    __slots__ = ("fpga_id", "type", "pack")
    FPGA_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PACK_FIELD_NUMBER: _ClassVar[int]
    fpga_id: str
    type: str
    pack: str
    def __init__(self, fpga_id: _Optional[str] = ..., type: _Optional[str] = ..., pack: _Optional[str] = ...) -> None: ...

class Ecp5FpgaInfo(_message.Message):
    __slots__ = ("type", "pack", "speed")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PACK_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    type: str
    pack: str
    speed: int
    def __init__(self, type: _Optional[str] = ..., pack: _Optional[str] = ..., speed: _Optional[int] = ...) -> None: ...

class GowinFpgaInfo(_message.Message):
    __slots__ = ("family",)
    FAMILY_FIELD_NUMBER: _ClassVar[int]
    family: str
    def __init__(self, family: _Optional[str] = ...) -> None: ...

class FpgaInfo(_message.Message):
    __slots__ = ("fpga_id", "part_num", "size", "ice40", "ecp5", "gowin")
    FPGA_ID_FIELD_NUMBER: _ClassVar[int]
    PART_NUM_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    ICE40_FIELD_NUMBER: _ClassVar[int]
    ECP5_FIELD_NUMBER: _ClassVar[int]
    GOWIN_FIELD_NUMBER: _ClassVar[int]
    fpga_id: str
    part_num: str
    size: str
    ice40: Ice40FpgaInfo
    ecp5: Ecp5FpgaInfo
    gowin: GowinFpgaInfo
    def __init__(self, fpga_id: _Optional[str] = ..., part_num: _Optional[str] = ..., size: _Optional[str] = ..., ice40: _Optional[_Union[Ice40FpgaInfo, _Mapping]] = ..., ecp5: _Optional[_Union[Ecp5FpgaInfo, _Mapping]] = ..., gowin: _Optional[_Union[GowinFpgaInfo, _Mapping]] = ...) -> None: ...

class Verbosity(_message.Message):
    __slots__ = ("all", "synth", "pnr")
    ALL_FIELD_NUMBER: _ClassVar[int]
    SYNTH_FIELD_NUMBER: _ClassVar[int]
    PNR_FIELD_NUMBER: _ClassVar[int]
    all: bool
    synth: bool
    pnr: bool
    def __init__(self, all: bool = ..., synth: bool = ..., pnr: bool = ...) -> None: ...

class Envrionment(_message.Message):
    __slots__ = ("platform_id", "debug", "yosys_path", "trellis_path")
    PLATFORM_ID_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FIELD_NUMBER: _ClassVar[int]
    YOSYS_PATH_FIELD_NUMBER: _ClassVar[int]
    TRELLIS_PATH_FIELD_NUMBER: _ClassVar[int]
    platform_id: str
    debug: bool
    yosys_path: str
    trellis_path: str
    def __init__(self, platform_id: _Optional[str] = ..., debug: bool = ..., yosys_path: _Optional[str] = ..., trellis_path: _Optional[str] = ...) -> None: ...

class Project(_message.Message):
    __slots__ = ("board_id", "top_module")
    BOARD_ID_FIELD_NUMBER: _ClassVar[int]
    TOP_MODULE_FIELD_NUMBER: _ClassVar[int]
    board_id: str
    top_module: str
    def __init__(self, board_id: _Optional[str] = ..., top_module: _Optional[str] = ...) -> None: ...

class CmdLintInfo(_message.Message):
    __slots__ = ("verilator_all", "verilator_no_style", "verilator_no_warn", "verilator_warn")
    VERILATOR_ALL_FIELD_NUMBER: _ClassVar[int]
    VERILATOR_NO_STYLE_FIELD_NUMBER: _ClassVar[int]
    VERILATOR_NO_WARN_FIELD_NUMBER: _ClassVar[int]
    VERILATOR_WARN_FIELD_NUMBER: _ClassVar[int]
    verilator_all: bool
    verilator_no_style: bool
    verilator_no_warn: _containers.RepeatedScalarFieldContainer[str]
    verilator_warn: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, verilator_all: bool = ..., verilator_no_style: bool = ..., verilator_no_warn: _Optional[_Iterable[str]] = ..., verilator_warn: _Optional[_Iterable[str]] = ...) -> None: ...

class CmdGraphInfo(_message.Message):
    __slots__ = ("graph_spec",)
    GRAPH_SPEC_FIELD_NUMBER: _ClassVar[int]
    graph_spec: str
    def __init__(self, graph_spec: _Optional[str] = ...) -> None: ...

class CmdSimInfo(_message.Message):
    __slots__ = ("test_bench",)
    TEST_BENCH_FIELD_NUMBER: _ClassVar[int]
    test_bench: str
    def __init__(self, test_bench: _Optional[str] = ...) -> None: ...

class CmdTestInfo(_message.Message):
    __slots__ = ("test_bench",)
    TEST_BENCH_FIELD_NUMBER: _ClassVar[int]
    test_bench: str
    def __init__(self, test_bench: _Optional[str] = ...) -> None: ...

class SconsParams(_message.Message):
    __slots__ = ("arch", "fpga_info", "verbosity", "envrionment", "project", "cmd_lint", "cmd_graph", "cmd_sim", "cmd_test")
    ARCH_FIELD_NUMBER: _ClassVar[int]
    FPGA_INFO_FIELD_NUMBER: _ClassVar[int]
    VERBOSITY_FIELD_NUMBER: _ClassVar[int]
    ENVRIONMENT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    CMD_LINT_FIELD_NUMBER: _ClassVar[int]
    CMD_GRAPH_FIELD_NUMBER: _ClassVar[int]
    CMD_SIM_FIELD_NUMBER: _ClassVar[int]
    CMD_TEST_FIELD_NUMBER: _ClassVar[int]
    arch: ApioArch
    fpga_info: FpgaInfo
    verbosity: Verbosity
    envrionment: Envrionment
    project: Project
    cmd_lint: CmdLintInfo
    cmd_graph: CmdGraphInfo
    cmd_sim: CmdSimInfo
    cmd_test: CmdTestInfo
    def __init__(self, arch: _Optional[_Union[ApioArch, str]] = ..., fpga_info: _Optional[_Union[FpgaInfo, _Mapping]] = ..., verbosity: _Optional[_Union[Verbosity, _Mapping]] = ..., envrionment: _Optional[_Union[Envrionment, _Mapping]] = ..., project: _Optional[_Union[Project, _Mapping]] = ..., cmd_lint: _Optional[_Union[CmdLintInfo, _Mapping]] = ..., cmd_graph: _Optional[_Union[CmdGraphInfo, _Mapping]] = ..., cmd_sim: _Optional[_Union[CmdSimInfo, _Mapping]] = ..., cmd_test: _Optional[_Union[CmdTestInfo, _Mapping]] = ...) -> None: ...
