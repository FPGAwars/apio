
# pylint: disable=C0114, C0115, C0301, C0303, C0411
# pylint: disable=E0245, E0602, E1139
# pylint: disable=R0913, R0801, R0917
# pylint: disable=W0212, W0223, W0311, W0613, W0622

from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApioArch(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ARCH_UNSPECIFIED: _ClassVar[ApioArch]
    ICE40: _ClassVar[ApioArch]
    ECP5: _ClassVar[ApioArch]
    GOWIN: _ClassVar[ApioArch]

class TerminalMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TERMINAL_UNSPECIFIED: _ClassVar[TerminalMode]
    AUTO_TERMINAL: _ClassVar[TerminalMode]
    FORCE_TERMINAL: _ClassVar[TerminalMode]
    FORCE_PIPE: _ClassVar[TerminalMode]

class GraphOutputType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TYPE_UNSPECIFIED: _ClassVar[GraphOutputType]
    SVG: _ClassVar[GraphOutputType]
    PNG: _ClassVar[GraphOutputType]
    PDF: _ClassVar[GraphOutputType]
ARCH_UNSPECIFIED: ApioArch
ICE40: ApioArch
ECP5: ApioArch
GOWIN: ApioArch
TERMINAL_UNSPECIFIED: TerminalMode
AUTO_TERMINAL: TerminalMode
FORCE_TERMINAL: TerminalMode
FORCE_PIPE: TerminalMode
TYPE_UNSPECIFIED: GraphOutputType
SVG: GraphOutputType
PNG: GraphOutputType
PDF: GraphOutputType

class Ice40FpgaInfo(_message.Message):
    __slots__ = ("type", "pack")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PACK_FIELD_NUMBER: _ClassVar[int]
    type: str
    pack: str
    def __init__(self, type: _Optional[str] = ..., pack: _Optional[str] = ...) -> None: ...

class Ecp5FpgaInfo(_message.Message):
    __slots__ = ("type", "pack", "speed")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PACK_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    type: str
    pack: str
    speed: str
    def __init__(self, type: _Optional[str] = ..., pack: _Optional[str] = ..., speed: _Optional[str] = ...) -> None: ...

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

class Environment(_message.Message):
    __slots__ = ("platform_id", "is_windows", "terminal_mode", "theme_name", "is_debug", "yosys_path", "trellis_path")
    PLATFORM_ID_FIELD_NUMBER: _ClassVar[int]
    IS_WINDOWS_FIELD_NUMBER: _ClassVar[int]
    TERMINAL_MODE_FIELD_NUMBER: _ClassVar[int]
    THEME_NAME_FIELD_NUMBER: _ClassVar[int]
    IS_DEBUG_FIELD_NUMBER: _ClassVar[int]
    YOSYS_PATH_FIELD_NUMBER: _ClassVar[int]
    TRELLIS_PATH_FIELD_NUMBER: _ClassVar[int]
    platform_id: str
    is_windows: bool
    terminal_mode: TerminalMode
    theme_name: str
    is_debug: bool
    yosys_path: str
    trellis_path: str
    def __init__(self, platform_id: _Optional[str] = ..., is_windows: bool = ..., terminal_mode: _Optional[_Union[TerminalMode, str]] = ..., theme_name: _Optional[str] = ..., is_debug: bool = ..., yosys_path: _Optional[str] = ..., trellis_path: _Optional[str] = ...) -> None: ...

class Project(_message.Message):
    __slots__ = ("board_id", "top_module", "yosys_synth_extra_options")
    BOARD_ID_FIELD_NUMBER: _ClassVar[int]
    TOP_MODULE_FIELD_NUMBER: _ClassVar[int]
    YOSYS_SYNTH_EXTRA_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    board_id: str
    top_module: str
    yosys_synth_extra_options: str
    def __init__(self, board_id: _Optional[str] = ..., top_module: _Optional[str] = ..., yosys_synth_extra_options: _Optional[str] = ...) -> None: ...

class LintParams(_message.Message):
    __slots__ = ("top_module", "verilator_all", "verilator_no_style", "verilator_no_warns", "verilator_warns")
    TOP_MODULE_FIELD_NUMBER: _ClassVar[int]
    VERILATOR_ALL_FIELD_NUMBER: _ClassVar[int]
    VERILATOR_NO_STYLE_FIELD_NUMBER: _ClassVar[int]
    VERILATOR_NO_WARNS_FIELD_NUMBER: _ClassVar[int]
    VERILATOR_WARNS_FIELD_NUMBER: _ClassVar[int]
    top_module: str
    verilator_all: bool
    verilator_no_style: bool
    verilator_no_warns: _containers.RepeatedScalarFieldContainer[str]
    verilator_warns: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, top_module: _Optional[str] = ..., verilator_all: bool = ..., verilator_no_style: bool = ..., verilator_no_warns: _Optional[_Iterable[str]] = ..., verilator_warns: _Optional[_Iterable[str]] = ...) -> None: ...

class GraphParams(_message.Message):
    __slots__ = ("output_type", "top_module")
    OUTPUT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TOP_MODULE_FIELD_NUMBER: _ClassVar[int]
    output_type: GraphOutputType
    top_module: str
    def __init__(self, output_type: _Optional[_Union[GraphOutputType, str]] = ..., top_module: _Optional[str] = ...) -> None: ...

class SimParams(_message.Message):
    __slots__ = ("testbench", "force_sim")
    TESTBENCH_FIELD_NUMBER: _ClassVar[int]
    FORCE_SIM_FIELD_NUMBER: _ClassVar[int]
    testbench: str
    force_sim: bool
    def __init__(self, testbench: _Optional[str] = ..., force_sim: bool = ...) -> None: ...

class ApioTestParams(_message.Message):
    __slots__ = ("testbench",)
    TESTBENCH_FIELD_NUMBER: _ClassVar[int]
    testbench: str
    def __init__(self, testbench: _Optional[str] = ...) -> None: ...

class UploadParams(_message.Message):
    __slots__ = ("programmer_cmd",)
    PROGRAMMER_CMD_FIELD_NUMBER: _ClassVar[int]
    programmer_cmd: str
    def __init__(self, programmer_cmd: _Optional[str] = ...) -> None: ...

class TargetParams(_message.Message):
    __slots__ = ("lint", "graph", "sim", "test", "upload")
    LINT_FIELD_NUMBER: _ClassVar[int]
    GRAPH_FIELD_NUMBER: _ClassVar[int]
    SIM_FIELD_NUMBER: _ClassVar[int]
    TEST_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_FIELD_NUMBER: _ClassVar[int]
    lint: LintParams
    graph: GraphParams
    sim: SimParams
    test: ApioTestParams
    upload: UploadParams
    def __init__(self, lint: _Optional[_Union[LintParams, _Mapping]] = ..., graph: _Optional[_Union[GraphParams, _Mapping]] = ..., sim: _Optional[_Union[SimParams, _Mapping]] = ..., test: _Optional[_Union[ApioTestParams, _Mapping]] = ..., upload: _Optional[_Union[UploadParams, _Mapping]] = ...) -> None: ...

class RichLibWindowsParams(_message.Message):
    __slots__ = ("vt", "truecolor")
    VT_FIELD_NUMBER: _ClassVar[int]
    TRUECOLOR_FIELD_NUMBER: _ClassVar[int]
    vt: bool
    truecolor: bool
    def __init__(self, vt: bool = ..., truecolor: bool = ...) -> None: ...

class SconsParams(_message.Message):
    __slots__ = ("timestamp", "arch", "fpga_info", "verbosity", "environment", "project", "target", "rich_lib_windows_params")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ARCH_FIELD_NUMBER: _ClassVar[int]
    FPGA_INFO_FIELD_NUMBER: _ClassVar[int]
    VERBOSITY_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    RICH_LIB_WINDOWS_PARAMS_FIELD_NUMBER: _ClassVar[int]
    timestamp: str
    arch: ApioArch
    fpga_info: FpgaInfo
    verbosity: Verbosity
    environment: Environment
    project: Project
    target: TargetParams
    rich_lib_windows_params: RichLibWindowsParams
    def __init__(self, timestamp: _Optional[str] = ..., arch: _Optional[_Union[ApioArch, str]] = ..., fpga_info: _Optional[_Union[FpgaInfo, _Mapping]] = ..., verbosity: _Optional[_Union[Verbosity, _Mapping]] = ..., environment: _Optional[_Union[Environment, _Mapping]] = ..., project: _Optional[_Union[Project, _Mapping]] = ..., target: _Optional[_Union[TargetParams, _Mapping]] = ..., rich_lib_windows_params: _Optional[_Union[RichLibWindowsParams, _Mapping]] = ...) -> None: ...
