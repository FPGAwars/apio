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

Required packages: ``scons``, ``icestorm``.

Options
-------

.. program:: apio build

.. option::
    -b, --board

Select a specific board.

.. option::
    --fpga

Select a specific FPGA.

.. option::
    --size --type --pack

Select a specific FPGA size, type and pack.

.. option::
    -p, --project-dir

Set the target directory for the project.

.. option::
    -v, --verbose

Show the entire output of the command.

.. option::
    --verbose-yosys

Show the yosys output of the command.

.. option::
    --verbose-arachne

Show the arachne output of the command.

.. option::
    --top-module

Set the top level module name used for build. Otherwise Yosys will auto select. 

.. note::

  All available boards, FPGAs, sizes, types and packs are showed in :ref:`cmd_boards`

Examples
--------

1. Process the *leds example*

.. code::

  $ apio build
  [] Processing icezum
  ---------------------------------------------------------------------------------------------
  yosys -p "synth_ice40 -blif hardware.blif" -q leds.v
  arachne-pnr -d 1k -P tq144 -p leds.pcf -o hardware.asc -q hardware.blif
  icepack hardware.asc hardware.bin
  ================================== [SUCCESS] Took 0.72 seconds ==============================

.. Executing: scons -Q build fpga_type=hx fpga_pack=tq144 fpga_size=1k -f /path/to/SConstruct
