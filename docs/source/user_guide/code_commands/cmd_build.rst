.. _cmd_build:

apio build
==========

.. contents::

Usage
-----

.. code::

    apio build [OPTIONS]

Description
-----------

Synthesize the bitstream: generates a **bin** file from a **verilog** and a **pcf** files.

This command requires the ``scons`` and ``icestorm`` packages.

Options
-------

.. program:: apio build

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

1. Process the *leds example*

.. code::

  $ apio build
  Info: use apio.ini board: icezum
  Using default SConstruct file
  [] Processing icezum
  -------------------------------------------------------------------------------------------------
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
  ================================== [SUCCESS] Took 0.99 seconds =================================

.. Executing: scons -Q build fpga_type=hx fpga_pack=tq144 fpga_size=1k -f /path/to/SConstruct
