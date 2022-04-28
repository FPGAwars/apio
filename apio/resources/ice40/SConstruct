# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# -- Generic Scons script for Sintesizing hardware on an FPGA and more.
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Authors Juan Gonzáles, Jesús Arroyo
# -- Licence GPLv2
# ----------------------------------------------------------------------

import os
import re
from platform import system

from SCons.Script import (Builder, DefaultEnvironment, Default, AlwaysBuild,
                          GetOption, Exit, COMMAND_LINE_TARGETS, ARGUMENTS,
                          Variables, Help, Glob)

# -- Load arguments
PROG = ARGUMENTS.get('prog', '')
FPGA_SIZE = ARGUMENTS.get('fpga_size', '')
FPGA_TYPE = ARGUMENTS.get('fpga_type', '')
FPGA_PACK = ARGUMENTS.get('fpga_pack', '')
VERBOSE_ALL = ARGUMENTS.get('verbose_all', False)
VERBOSE_YOSYS = ARGUMENTS.get('verbose_yosys', False)
VERBOSE_PNR = ARGUMENTS.get('verbose_pnr', False)
VERILATOR_ALL = ARGUMENTS.get('all', False)
VERILATOR_NO_STYLE = ARGUMENTS.get('nostyle', False)
VERILATOR_NO_WARN = ARGUMENTS.get('nowarn', '').split(',')
VERILATOR_WARN = ARGUMENTS.get('warn', '').split(',')
VERILATOR_TOP = ARGUMENTS.get('top', '')
VERILATOR_PARAM_STR = ''
for warn in VERILATOR_NO_WARN:
    if warn != '':
        VERILATOR_PARAM_STR += ' -Wno-' + warn

for warn in VERILATOR_WARN:
    if warn != '':
        VERILATOR_PARAM_STR += ' -Wwarn-' + warn

# -- Size. Possible values: 1k, 8k
# -- Type. Possible values: hx, lp
# -- Package. Possible values: swg16tr, cm36, cm49, cm81, cm121, cm225, qn84,
# --   cb81, cb121, cb132, vq100, tq144, ct256

# -- Add the FPGA flags as variables to be shown with the -h scons option
vars = Variables()
vars.Add('fpga_size', 'Set the ICE40 FPGA size (1k/8k)', FPGA_SIZE)
vars.Add('fpga_type', 'Set the ICE40 FPGA type (hx/lp)', FPGA_TYPE)
vars.Add('fpga_pack', 'Set the ICE40 FPGA packages', FPGA_PACK)

# -- Create environment
env = DefaultEnvironment(ENV=os.environ,
                         tools=[],
                         variables=vars)

# -- Show all the flags defined, when scons is invoked with -h
Help(vars.GenerateHelpText(env))

# -- Just for debugging
if 'build' in COMMAND_LINE_TARGETS or \
   'upload' in COMMAND_LINE_TARGETS or \
   'time' in COMMAND_LINE_TARGETS:

    # print('FPGA_SIZE: {}'.format(FPGA_SIZE))
    # print('FPGA_TYPE: {}'.format(FPGA_TYPE))
    # print('FPGA_PACK: {}'.format(FPGA_PACK))

    if 'upload' in COMMAND_LINE_TARGETS:

        if PROG == '':
            print('Error: no programmer command found')
            Exit(1)

        # print('PROG: {}'.format(PROG))

# -- Resources paths
IVL_PATH = os.environ['IVL'] if 'IVL' in os.environ else ''
ICEBOX_PATH = os.environ['ICEBOX'] if 'ICEBOX' in os.environ else ''
CHIPDB_PATH = os.path.join(ICEBOX_PATH, 'chipdb-{0}.txt'.format(FPGA_SIZE))
YOSYS_PATH = os.environ['YOSYS_LIB'] if 'YOSYS_LIB' in os.environ else ''

isWindows = 'Windows' == system()
VVP_PATH = '' if isWindows or not IVL_PATH else '-M "{0}"'.format(IVL_PATH)
IVER_PATH = '' if isWindows or not IVL_PATH else '-B "{0}"'.format(IVL_PATH)

# -- Target name
TARGET = 'hardware'

# -- Scan required .list files
list_files_re = re.compile(r'[\n|\s][^\/]?\"(.*\.list?)\"', re.M)


def list_files_scan(node, env, path):
    contents = node.get_text_contents()
    includes = list_files_re.findall(contents)
    return env.File(includes)


list_scanner = env.Scanner(function=list_files_scan)

# -- Get a list of all the verilog files in the src folfer, in ASCII, with
# -- the full path. All these files are used for the simulation
v_nodes = Glob('*.v')
src_sim = [str(f) for f in v_nodes]

# --------- Get the Testbench file (there should be only 1)
# -- Create a list with all the files finished in _tb.v. It should contain
# -- the test bench
list_tb = [f for f in src_sim if f[-5:].upper() == '_TB.V']

if len(list_tb) > 1:
    print('Warning: more than one testbenches used')

# -- Error checking
try:
    testbench = list_tb[0]

# -- there is no testbench
except IndexError:
    testbench = None

SIMULNAME = ''
TARGET_SIM = ''

# clean
if len(COMMAND_LINE_TARGETS) == 0:
    if testbench is not None:
        # -- Simulation name
        SIMULNAME, ext = os.path.splitext(testbench)
# sim
elif 'sim' in COMMAND_LINE_TARGETS:
    if testbench is None:
        print('Error: no testbench found for simulation')
        Exit(1)

    # -- Simulation name
    SIMULNAME, ext = os.path.splitext(testbench)

# -- Target sim name
if SIMULNAME:
    TARGET_SIM = SIMULNAME  # .replace('\\', '\\\\')

# -------- Get the synthesis files.  They are ALL the files except the
# -------- testbench
src_synth = [f for f in src_sim if f not in list_tb]

if len(src_synth) == 0:
    print('Error: no verilog files found (.v)')
    Exit(1)

# -- For debugging
# print('Testbench: {}'.format(testbench))
# print('SIM NAME: {}'.format(SIMULNAME))

# -- Get the PCF file
PCF = ''
PCF_list = Glob('*.pcf')

try:
    PCF = PCF_list[0]
except IndexError:
    print('\n---> WARNING: no PCF file found (.pcf)\n')

# -- Debug
# print('PCF Found: {}'.format(PCF))

# -- Define the Sintesizing Builder
synth = Builder(
    action='yosys -p \"synth_ice40 -json $TARGET\" {} $SOURCES'.format(
        '' if VERBOSE_ALL or VERBOSE_YOSYS else '-q'
    ),
    suffix='.json',
    src_suffix='.v',
    source_scanner=list_scanner)

pnr = Builder(
    action='nextpnr-ice40 --{0}{1} --package {2} --json $SOURCE --asc $TARGET --pcf {3} {4}'.format(
        FPGA_TYPE, FPGA_SIZE, FPGA_PACK, PCF,
        '' if VERBOSE_ALL or VERBOSE_PNR else '-q'),
    suffix='.asc',
    src_suffix='.json')

bitstream = Builder(
    action='icepack $SOURCE $TARGET',
    suffix='.bin',
    src_suffix='.asc')

# -- Icetime builder
# https://github.com/cliffordwolf/icestorm/issues/57
time_rpt = Builder(
    action='icetime -d {0}{1} -P {2} -C "{3}" -mtr $TARGET $SOURCE'.format(
        FPGA_TYPE, FPGA_SIZE, FPGA_PACK, CHIPDB_PATH),
    suffix='.rpt',
    src_suffix='.asc')

# -- Build the environment
env.Append(BUILDERS={
    'Synth': synth, 'PnR': pnr, 'Bin': bitstream, 'Time': time_rpt})

# -- Generate the bitstream
blif = env.Synth(TARGET, [src_synth])
asc = env.PnR(TARGET, [blif, PCF])
bitstream = env.Bin(TARGET, asc)

build = env.Alias('build', bitstream)
AlwaysBuild(build)

# -- Upload the bitstream into FPGA
upload = env.Alias('upload', bitstream, '{0} $SOURCE'.format(PROG))
AlwaysBuild(upload)

# -- Target time: calculate the time
rpt = env.Time(asc)
t = env.Alias('time', rpt)
AlwaysBuild(t)

# -- Icarus Verilog builders
iverilog = Builder(
    action='iverilog {0} -o $TARGET -D VCD_OUTPUT={1} -D NO_ICE40_DEFAULT_ASSIGNMENTS "{2}/ice40/cells_sim.v" $SOURCES'.format(
        IVER_PATH, TARGET_SIM, YOSYS_PATH),
    suffix='.out',
    src_suffix='.v',
    source_scanner=list_scanner)

# NOTE: output file name is defined in the iverilog call using VCD_OUTPUT macro
vcd = Builder(
    action='vvp {0} $SOURCE'.format(
        VVP_PATH),
    suffix='.vcd',
    src_suffix='.out')

env.Append(BUILDERS={'IVerilog': iverilog, 'VCD': vcd})

# --- Verify
vout = env.IVerilog(TARGET, src_synth)

verify = env.Alias('verify', vout)
AlwaysBuild(verify)

# --- Simulation
sout = env.IVerilog(TARGET_SIM, src_sim)
vcd_file = env.VCD(sout)

waves = env.Alias('sim', vcd_file, 'gtkwave {0} {1}.gtkw'.format(
    vcd_file[0], SIMULNAME))
AlwaysBuild(waves)

# -- Verilator builder
verilator = Builder(
    action='verilator --lint-only -Wno-TIMESCALEMOD -v {0}/ice40/cells_sim.v {1} {2} {3} {4} $SOURCES'.format(
        YOSYS_PATH,
        '-Wall' if VERILATOR_ALL else '',
        '-Wno-style' if VERILATOR_NO_STYLE else '',
        VERILATOR_PARAM_STR if VERILATOR_PARAM_STR else '',
        '--top-module ' + VERILATOR_TOP if VERILATOR_TOP else ''),
    src_suffix='.v',
    source_scanner=list_scanner)

env.Append(BUILDERS={'Verilator': verilator})

# --- Lint
lout = env.Verilator(TARGET, src_synth)

lint = env.Alias('lint', lout)
AlwaysBuild(lint)

Default(bitstream)

# -- These is for cleaning the files generated using the alias targets
if GetOption('clean'):
    env.Default([t, vout, sout, vcd_file])
