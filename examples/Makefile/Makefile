#-----------------------------------------------------------------------------
#-- Generic Makefile for building FPGA projects using make
#--
#------------------------------------------------------------------------------
#--         HOW TO USE
#--
#-------- TOOLS INSTALLATION
#--
#--  Make sure all the tools are in the PATH
#--
#-- Bitstream generation:
#-- icestorm tools: http://www.clifford.at/icestorm/
#--    (yosys, arachne-prn, icepack, iceprog, icetime)
#--
#-- For simulating:
#--  icarus verilog: http://iverilog.icarus.com/
#--  gtkwave: http://gtkwave.sourceforge.net/
#--
#------- CONFIGURATION:
#-- Change the variable NAME with the name of the main file (ej. leds)
#-- Change the variable DEPS with the name of the verilog files that are
#--   needed for building (ej. uart.v timer.v)
#--
#-- Modify the FPGA_SIZE, FPGA_TYPE and FPGA_PACK variables for
#--  configuring the target board
#--
#-- This variables can also be set during the call to make:
#-- ex:   make sint FPGA_PACK=vq100
#--
#------- GENERATING THE BITSTREAM
#--
#--  make sint
#--
#--  It creates the example.bin bitstream. Ready for uploading into the FPGA
#--
#-------- UPLOADING INTO THE FPGA
#--
#--  make prog
#--
#-------- SIMULATING
#--
#--  make sim
#--
#-------- TIME CALCULATIONS
#--
#--  make time
#------------------------------------------------------------------------------
#--         MANUAL BUILD  (no make)
#------------------------------------------------------------------------------
#-- This is just for documentation purposes
#
#------- GENERATING THE BISTREAM ---------------------------------------------
#--
#--  The "manual" building of an example called "example" from verilog to
#--  bitstream can be done executing the following tools:
#--  (for icestick or icezum alhambra boards)
#--
#--  $ yosys -p "synth_ice40 -blif example.blif" example.v
#--  $ arachne-pnr -d 1k -P tq144 -p example.pcf example.blif -o example.asc
#--  $ icepack example.asc example.bin
#--
#--  For uploading the bitstream into the FPGA:
#--  $ icepog example.bin
#--
#--------- CHECKING the time -------------------------------------------------
#--  $ icetime -d hx1k -P tq144 -mtr example.rpt example.asc
#--
#--------- SIMULATION --------------------------------------------------------
#--  For simulating the following tools should be installed:
#--
#--  icarus verilog: http://iverilog.icarus.com/
#--  gtkwave: http://gtkwave.sourceforge.net/
#--
#--  Let's say we have the example.v and example_tb.v files.
#--  The manual process for simulating a testbench is:
#--
#--  Generate an executable file from the testbench:
#--  iverilog example_tb.v example.v -o example_tb.out
#--
#--  Execute it
#--  ./leds_tb.out
#--
#--  Show the results:
#--  gtkwave example_tv.vcd example_tb.gtkw
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#--- CONFIGURATION:  Set the project name (top level entity without extension)
#--  and the dependencies (verilog files with .v extension)
#--  DEPS can be set blank, if no dependencies
#--  or it should contain the dependencies for the top entity:
#--  Ex. DEPS = uart.v timer.v
#------------------------------------------------------------------------------
NAME = leds
DEPS =

#-----------------------------------------------------------------------------
#-- FLAGs:
#--
#-- Default values compatible with the icestick and icezum alhambra boards
#--
#-----------------------------------------------------------------------------
#-------- Icestick / IceZUM Alhambra boards:
#-- FPGA_SIZE = 1k
#-- FPGA_TYPE = hx
#-- FPGA_PACK = tq144
#
#-------- Nandland go board
#-- FPGA_SIZE = 1k
#-- FPGA_TYPE = hx
#-- FPGA_PACK = vq100
#--
#-----------------------------------------------------------------------------
#-- Size. Possible values: 1k, 8k
FPGA_SIZE = 1k

#-- Type. Possible values: hx, lp
FPGA_TYPE = hx

#-- Package. Possible values: swg16tr, cm36, cm49, cm81, cm121, cm225, qn84,
#--   cb81, cb121, cb132, vq100, tq144, ct256
FPGA_PACK = tq144

#------------- Simulation of project 1 ---------
sim: $(NAME)_tb.vcd
	gtkwave $< $(<:.vcd=.gtkw) &

#-- set the dependencies for simulation
$(NAME)_tb.vcd: $(NAME).v $(DEPS) $(NAME)_tb.v

#---- Synthesis of project 1 ------------------
sint: $(NAME).bin

#-- Set the dependencies for synthetization
$(NAME).blif: $(NAME).v $(DEPS)

#-- Set the dependencies for the place and route
$(NAME).asc: $(NAME).blif $(NAME).pcf

#---- Upload into FPGA of project 1 ------
prog: $(NAME).bin
	iceprog $<

# --- Time report
time: $(NAME).rpt


#--------------------------------
#-- General Compilation rules
#--------------------------------

.SUFFIXES: .asc .bin .blif .v .vcd .rpt

# -- Rule for generating time reports
.asc.rpt:
	icetime -d $(FPGA_TYPE)$(FPGA_SIZE) -P $(FPGA_PACK) -mtr $@ $^

#-- Rule for generating the simulations
.v.vcd:
		iverilog $^ -o $(@:.vcd=.out)
		./$(@:.vcd=.out)

#-- Rule to perform the synthesis
.v.blif:
	yosys -p "synth_ice40 -blif $@" $^

#-- Rule to perform the place and route
#-- The .pcf file should have the same name than the .blif file
.blif.asc:
	arachne-pnr -d $(FPGA_SIZE) -P $(FPGA_PACK) -p $(@:.asc=.pcf) $< -o $@

#-- Rule to obtain the .bin bitstream from the .txt ascii files
.asc.bin:
	icepack $< $@

#-- Clean the project
clean:
	rm -f *.bin *.asc *.blif *.out *.vcd examples/*~ *.rpt

.PHONY: all clean time
