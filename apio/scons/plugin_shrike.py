# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

"""Apio scons plugin for the Shrike (SLG47910V / ForgeFPGA) architecture."""

# pylint: disable=duplicate-code

import base64
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

from SCons.Action import Action
from SCons.Builder import BuilderBase, CompositeBuilder
from SCons.Script import Builder

from apio.common.common_util import SRC_SUFFIXES
from apio.scons.apio_env import ApioEnv
from apio.scons.plugin_base import ArchPluginInfo, PluginBase
from apio.scons.plugin_util import (
    announce_testbench_action,
    basename,
    has_testbench_name,
    iverilog_action,
    make_verilator_config_builder,
    source_files_issue_scanner_action,
    verilator_lint_action,
)

# ── Go Configure Software Hub toolchain paths ─────────────────────────────────
_GCSW = Path("/opt/go-configure-sw-hub/bin/external")
_YOSYS = str(_GCSW / "yosys/v59/yosys")
_EDA_PLACER = str(_GCSW / "eda-placer/v23/eda-placer")
_EFLX_COMPILER_INSTALL = str(_GCSW / "eda-placer/v23")

# ── PNR flags (captured from GUI strace) ─────────────────────────────────────
# Order matches the Go Configure GUI invocation exactly.
_PNR_FLAGS = [
    ("-ENABLE_BITSTREAM_OUTPUT_AXI",     "1"),
    ("-ENABLE_BITSTREAM_OUTPUT_AXI_CRC", "0"),
    ("-ENABLE_HIGH_DENSITY_PACKING",     "1"),
    ("-ENABLE_HIGH_DENSITY_IO_PACKING",  "0"),
    ("-CLK_CONCURRENT_OPT",              "1"),
    ("-PLACE_AND_TRIAL_ROUTE",           "0"),
    ("-PNR_TRIAL_ITER_TOTAL",            "20"),
    ("-MAX_ROUTE_ITER",                  "300"),
    ("-MAX_CPU",                         None),  # filled at runtime
    ("-TIMING_ANALYSIS_CORNER",          "0"),
]

# ── SLG47910V Rev BB bitstream fixed headers ──────────────────────────────────
_FMEM_HEADER = [
    0xAA22FF11, 0x00000000,
    0x22222222, 0x22222222, 0x22220000,
    0x03000000,
    0x00000000, 0x00000000, 0x00000000, 0x00000000,
]
_OTP_HEADER = [
    0x00000028, 0x00000000,
    0xA5A5A5A5, 0x00000000, 0x00000000,
    0x5A5A5A5A, 0x00000000,
] + _FMEM_HEADER[2:10]   # 15 words total
_MCU_PRE  = 320            # zero words before FLASH_MEM content
_MCU_POST = 8              # zero words after


# ── Inlined gen_fpga_data logic ───────────────────────────────────────────────

def _encode_fpga_data(netlist: str, fp: str, io: str) -> str:
    """Build the FPGA_DATA base64 blob that eda-placer expects as argv[2]."""
    max_cpu = str(os.cpu_count() or 1)
    eda_args = ["-edif", os.path.abspath(netlist), "-fp", os.path.abspath(fp)]
    for flag, val in _PNR_FLAGS:
        eda_args.append(flag)
        eda_args.append(max_cpu if val is None else val)
    eda_args += ["-io", os.path.abspath(io)]

    encoded = [a.encode("utf-8") for a in eda_args]
    inner  = struct.pack(">I", len(encoded))
    inner += b"".join(struct.pack(">I", len(e)) for e in encoded)
    inner += b"".join(encoded)
    outer  = struct.pack(">I", len(inner)) + zlib.compress(inner)
    return base64.b64encode(outer).decode("ascii")


# ── Inlined gen_bitstreams logic ──────────────────────────────────────────────

def _read_axi(path: Path) -> list:
    """Parse EFLX_bitstream_AXI.log: 1024×11 hex 32-bit words."""
    return [
        int(line.strip(), 16)
        for line in path.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _bswap32(w: int) -> int:
    return struct.unpack("<I", struct.pack(">I", w))[0]


def _write_bin(path: Path, words: list) -> None:
    path.write_bytes(struct.pack(f">{len(words)}I", *words))


# ── Helper ────────────────────────────────────────────────────────────────────

def _locate(candidates: list) -> str | None:
    """Return the first existing path from a list, or None."""
    for p in candidates:
        if Path(p).exists():
            return str(p)
    return None


class PluginShrike(PluginBase):
    """Apio scons plugin for the Shrike (SLG47910V / ForgeFPGA) architecture."""

    def __init__(self, apio_env: ApioEnv):
        super().__init__(apio_env)
        # No architecture simulation library needed for Shrike.
        self.sim_lib_files  = []
        self.lint_lib_files = []

    def plugin_info(self) -> ArchPluginInfo:
        return ArchPluginInfo(
            constrains_file_suffix=".pcf",   # io_map.pcf tracks IO changes
            pnr_file_suffix=".axi",          # sentinel file for the AXI log
            bitstream_file_suffix=".bin",    # FLASH_MEM format bitstream
        )

    # @overrides
    def synth_builder(self) -> BuilderBase | CompositeBuilder:
        """Write synth_script.ys then run Yosys v59 → hardware.edif."""
        apio_env   = self.apio_env
        params     = apio_env.params
        build_path = apio_env.env_build_path
        top        = params.apio_env_params.top_module

        def synth_action(target, source, env):
            _ = env

            # Absolute source paths so Yosys finds them regardless of cwd.
            src_paths = " ".join(
                f'"{Path(str(s)).resolve()}"'
                for s in source
                if str(s).endswith((".v", ".sv"))
            )
            if not src_paths:
                print("ERROR: no Verilog source files found.", file=sys.stderr)
                return 1

            edif_name = Path(str(target[0])).name   # e.g. "hardware.edif"

            script = "\n".join([
                f"read_verilog -sv {src_paths}",
                "hierarchy -check",
                "flatten -noscopeinfo",
                f"synth_xilinx -nobram -noiopad -nodsp -abc9 -top {top}",
                "clean",
                "autoname",
                'write_verilog "post_synth_results.v"',
                f'write_edif "{edif_name}"',
                "tee -q -o post_synth_report.txt stat",
            ])

            (build_path / "synth_script.ys").write_text(script)

            result = subprocess.run(
                [_YOSYS, "-e", "(.*)is implicitly declared.", "-Q",
                 "-s", "synth_script.ys"],
                cwd=str(build_path),
            )
            return result.returncode

        return Builder(
            action=Action(synth_action, "Shrike Synthesis (Yosys v59)"),
            suffix=".edif",
            src_suffix=SRC_SUFFIXES,
            source_scanner=self.verilog_src_scanner,
        )

    # @overrides
    def pnr_builder(self) -> BuilderBase | CompositeBuilder:
        """Encode FPGA_DATA blob, run eda-placer v23 → hardware.axi sentinel."""
        apio_env    = self.apio_env
        build_path  = apio_env.env_build_path
        # scons_manager.py calls os.chdir(project_dir) before SCons starts.
        project_dir = Path.cwd()

        def pnr_action(target, source, env):
            _ = env

            # source[0] = hardware.edif   source[1] = io_map.pcf (dependency)
            netlist = str(source[0])

            # io_spec_in.txt and floorplanspec.fp may live in the project root
            # (Apio-native project) or in ffpga/build/ (shrike-gen project).
            fp = _locate([
                project_dir / "floorplanspec.fp",
                project_dir / "ffpga" / "build" / "floorplanspec.fp",
            ])
            io = _locate([
                project_dir / "io_spec_in.txt",
                project_dir / "ffpga" / "build" / "io_spec_in.txt",
            ])

            for val, label in [(netlist, "netlist.edif"),
                               (fp,      "floorplanspec.fp"),
                               (io,      "io_spec_in.txt")]:
                if not val:
                    print(f"ERROR: required file not found: {label}",
                          file=sys.stderr)
                    return 1

            blob = _encode_fpga_data(netlist, fp, io)

            rundir = Path(tempfile.mkdtemp(prefix="eflx_"))
            try:
                out_dir = rundir / "out"
                out_dir.mkdir()

                env_vars = os.environ.copy()
                env_vars["EFLX_COMPILER_INSTALL"] = _EFLX_COMPILER_INSTALL

                log_path = build_path / "PNR_STDOUT.log"
                with log_path.open("w") as log_f:
                    result = subprocess.run(
                        [_EDA_PLACER, "FPGA_DATA", blob, "0"],
                        cwd=str(out_dir),
                        env=env_vars,
                        stdout=log_f,
                        stderr=subprocess.STDOUT,
                    )

                if result.returncode != 0:
                    print(f"ERROR: eda-placer failed — see {log_path}",
                          file=sys.stderr)
                    return result.returncode

                # Copy regular eda-placer output files to the Apio build dir.
                # eda-placer may also create directories such as "ta_message";
                # those are auxiliary output and must not be passed to shutil.copy().
                for f in out_dir.iterdir():
                    if f.is_file():
                        shutil.copy2(str(f), str(build_path / f.name))

                # Write the SCons sentinel (hardware.axi) using the AXI log.
                axi_src  = build_path / "EFLX_bitstream_AXI.log"
                sentinel = Path(str(target[0]))
                if axi_src.exists():
                    shutil.copy(str(axi_src), str(sentinel))
                else:
                    sentinel.write_text("# eda-placer AXI sentinel\n")

            finally:
                shutil.rmtree(str(rundir), ignore_errors=True)

            return 0

        return Builder(
            action=Action(pnr_action, "Shrike Place-and-Route (eda-placer v23)"),
            suffix=".axi",
            src_suffix=".edif",
        )

    # @overrides
    def bitstream_builder(self) -> BuilderBase | CompositeBuilder:
        """Parse EFLX_bitstream_AXI.log → hardware.bin (FLASH_MEM format)."""
        apio_env   = self.apio_env
        build_path = apio_env.env_build_path

        def bitstream_action(target, source, env):
            _ = env

            axi_path = build_path / "EFLX_bitstream_AXI.log"
            if not axi_path.exists():
                print(f"ERROR: AXI log not found: {axi_path}", file=sys.stderr)
                return 1

            axi      = _read_axi(axi_path)
            bswapped = [_bswap32(w) for w in axi]

            fmem = _FMEM_HEADER + bswapped
            mcu  = [0] * _MCU_PRE + fmem + [0] * _MCU_POST
            otp  = _OTP_HEADER + bswapped

            # Primary output tracked by SCons (FLASH_MEM format).
            _write_bin(Path(str(target[0])), mcu)

            # Secondary outputs alongside it.
            _write_bin(build_path / "hardware_fpga.bin", fmem)
            _write_bin(build_path / "FPGA_bitstream_OTP.bin", otp)

            print(f"Bitstream: {Path(str(target[0])).name} "
                  f"(+ MCU and OTP variants)")
            return 0

        return Builder(
            action=Action(bitstream_action, "Shrike Bitstream Generation"),
            suffix=".bin",
            src_suffix=".axi",
        )

    # @overrides
    def testbench_compile_builder(self) -> BuilderBase | CompositeBuilder:
        """Testbench compile using iverilog (no Shrike-specific lib needed)."""
        apio_env = self.apio_env
        params   = apio_env.params

        assert apio_env.targeting_one_of("sim", "test")
        assert (params.target.HasField("sim") or
                params.target.HasField("test"))

        def action_generator(target, source, env, for_signature):
            _ = (source, env, for_signature)
            testbench_file = str(target[0])
            assert has_testbench_name(testbench_file), testbench_file
            testbench_name = basename(testbench_file)
            return [
                announce_testbench_action(),
                source_files_issue_scanner_action(),
                iverilog_action(
                    apio_env,
                    verbose=params.verbosity.all,
                    vcd_output_name=testbench_name,
                    is_interactive=apio_env.targeting_one_of("sim"),
                    lib_dirs=[],
                    lib_files=[],
                ),
            ]

        return Builder(
            generator=action_generator,
            suffix=".out",
            src_suffix=SRC_SUFFIXES,
            source_scanner=self.verilog_src_scanner,
        )

    # @overrides
    def lint_config_builder(self) -> BuilderBase:
        """Lint config — no Shrike-specific primitives need suppression."""
        assert self.apio_env.targeting_one_of("lint")
        # Pass current dir as lib dir; no rules to suppress.
        return make_verilator_config_builder(Path("."), rules_to_supress=[])

    # @overrides
    def lint_builder(self) -> BuilderBase | CompositeBuilder:
        """Lint using system verilator (best-effort; requires v4.200+)."""
        return Builder(
            action=verilator_lint_action(
                self.apio_env, lib_dirs=[], lib_files=[]
            ),
            src_suffix=SRC_SUFFIXES,
            source_scanner=self.verilog_src_scanner,
        )
