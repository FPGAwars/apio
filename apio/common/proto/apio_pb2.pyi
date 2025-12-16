
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
    __slots__ = ("platform_id", "is_windows", "terminal_mode", "theme_name", "debug_level", "yosys_path", "trellis_path", "scons_shell_id")
    PLATFORM_ID_FIELD_NUMBER: _ClassVar[int]
    IS_WINDOWS_FIELD_NUMBER: _ClassVar[int]
    TERMINAL_MODE_FIELD_NUMBER: _ClassVar[int]
    THEME_NAME_FIELD_NUMBER: _ClassVar[int]
    DEBUG_LEVEL_FIELD_NUMBER: _ClassVar[int]
    YOSYS_PATH_FIELD_NUMBER: _ClassVar[int]
    TRELLIS_PATH_FIELD_NUMBER: _ClassVar[int]
    SCONS_SHELL_ID_FIELD_NUMBER: _ClassVar[int]
    platform_id: str
    is_windows: bool
    terminal_mode: TerminalMode
    theme_name: str
    debug_level: int
    yosys_path: str
    trellis_path: str
    scons_shell_id: str
    def __init__(self, platform_id: _Optional[str] = ..., is_windows: bool = ..., terminal_mode: _Optional[_Union[TerminalMode, str]] = ..., theme_name: _Optional[str] = ..., debug_level: _Optional[int] = ..., yosys_path: _Optional[str] = ..., trellis_path: _Optional[str] = ..., scons_shell_id: _Optional[str] = ...) -> None: ...

class ApioEnvParams(_message.Message):
    __slots__ = ("env_name", "board_id", "top_module", "defines", "yosys_synth_extra_options", "nextpnr_extra_options", "constraint_file")
    ENV_NAME_FIELD_NUMBER: _ClassVar[int]
    BOARD_ID_FIELD_NUMBER: _ClassVar[int]
    TOP_MODULE_FIELD_NUMBER: _ClassVar[int]
    DEFINES_FIELD_NUMBER: _ClassVar[int]
    YOSYS_SYNTH_EXTRA_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    NEXTPNR_EXTRA_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CONSTRAINT_FILE_FIELD_NUMBER: _ClassVar[int]
    env_name: str
    board_id: str
    top_module: str
    defines: _containers.RepeatedScalarFieldContainer[str]
    yosys_synth_extra_options: _containers.RepeatedScalarFieldContainer[str]
    nextpnr_extra_options: _containers.RepeatedScalarFieldContainer[str]
    constraint_file: str
    def __init__(self, env_name: _Optional[str] = ..., board_id: _Optional[str] = ..., top_module: _Optional[str] = ..., defines: _Optional[_Iterable[str]] = ..., yosys_synth_extra_options: _Optional[_Iterable[str]] = ..., nextpnr_extra_options: _Optional[_Iterable[str]] = ..., constraint_file: _Optional[str] = ...) -> None: ...

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
    __slots__ = ("output_type", "top_module", "open_viewer")
    OUTPUT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TOP_MODULE_FIELD_NUMBER: _ClassVar[int]
    OPEN_VIEWER_FIELD_NUMBER: _ClassVar[int]
    output_type: GraphOutputType
    top_module: str
    open_viewer: bool
    def __init__(self, output_type: _Optional[_Union[GraphOutputType, str]] = ..., top_module: _Optional[str] = ..., open_viewer: bool = ...) -> None: ...

class SimParams(_message.Message):
    __slots__ = ("testbench", "force_sim", "no_gtkwave", "detach_gtkwave")
    TESTBENCH_FIELD_NUMBER: _ClassVar[int]
    FORCE_SIM_FIELD_NUMBER: _ClassVar[int]
    NO_GTKWAVE_FIELD_NUMBER: _ClassVar[int]
    DETACH_GTKWAVE_FIELD_NUMBER: _ClassVar[int]
    testbench: str
    force_sim: bool
    no_gtkwave: bool
    detach_gtkwave: bool
    def __init__(self, testbench: _Optional[str] = ..., force_sim: bool = ..., no_gtkwave: bool = ..., detach_gtkwave: bool = ...) -> None: ...

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

class SconsParams(_message.Message):
    __slots__ = ("timestamp", "arch", "fpga_info", "verbosity", "environment", "apio_env_params", "target")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ARCH_FIELD_NUMBER: _ClassVar[int]
    FPGA_INFO_FIELD_NUMBER: _ClassVar[int]
    VERBOSITY_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    APIO_ENV_PARAMS_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    timestamp: str
    arch: ApioArch
    fpga_info: FpgaInfo
    verbosity: Verbosity
    environment: Environment
    apio_env_params: ApioEnvParams
    target: TargetParams
    def __init__(self, timestamp: _Optional[str] = ..., arch: _Optional[_Union[ApioArch, str]] = ..., fpga_info: _Optional[_Union[FpgaInfo, _Mapping]] = ..., verbosity: _Optional[_Union[Verbosity, _Mapping]] = ..., environment: _Optional[_Union[Environment, _Mapping]] = ..., apio_env_params: _Optional[_Union[ApioEnvParams, _Mapping]] = ..., target: _Optional[_Union[TargetParams, _Mapping]] = ...) -> None: ...
