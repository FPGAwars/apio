.. _cmd_time:

apio time
=========

.. contents::

Usage
-----

.. code::

    apio time [OPTIONS]

Description
-----------

Bitstream timing analysis: generates a **rpt** file with a topological timing analysis report, from a **verilog** and a **pcf** files.

This command requires the ``scons`` and ``icestorm`` packages.

Options
-------

.. program:: apio time

.. option::
    --board

Select a specific board.

.. option::
    --fpga

Select a specific FPGA.

.. option::
    --size --type --pack

Select a specific FPGA size, type and pack.

.. note::

  All available boards, FPGAs, sizes, types and packs are showed in :ref:`cmd_boards`

Examples
--------

1. Timing analysis for the *leds example*

.. code::

  $ apio time
  Info: use apio.ini board: icezum
  Using default SConstruct file
  [] Processing icezum
  -------------------------------------------------------------------------------------------------
  Executing: scons -Q time fpga_type=hx fpga_pack=tq144 fpga_size=1k -f /path/to/SConstruct
  FPGA_SIZE: 1k
  FPGA_TYPE: hx
  FPGA_PACK: tq144
  [ ... ]
  After placement:
  PIOs       3 / 96
  PLBs       1 / 160
  BRAMs      0 / 16

  place time 0.00s
  route...
  pass 1, 0 shared.

  After routing:
  span_4     0 / 6944
  span_12    2 / 1440

  route time 0.01s
  write_txt hardware.asc...
  // Creating timing netlist..
  // Timing estimate: 0.24 ns (4161.98 MHz)
  ================================== [SUCCESS] Took 1.10 seconds =================================


  $ cat hardware.rpt

  icetime topological timing analysis report
  ==========================================

  Warning: This timing analysis report is an estimate!
  Info: max_span_hack is enabled: estimate is conservative.

  Report for critical path:
  -------------------------

          pre_io_13_11_0 (PRE_IO) [clk] -> PADOUT: 0.240 ns
       0.240 ns io_pad_13_11_0_din

  Total number of logic levels: 0
  Total path delay: 0.24 ns (4161.98 MHz)
