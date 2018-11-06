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

Required packages: ``scons``, ``icestorm``.

Options
-------

.. program:: apio time

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

.. note::

  All available boards, FPGAs, sizes, types and packs are showed in :ref:`cmd_boards`

Examples
--------

1. Timing analysis for the *leds example*

.. code::

  $ apio time
  [] Processing icezum
  ---------------------------------------------------------------------------------------------
  [...]
  // Reading input .asc file..
  // Reading 1k chipdb file..
  // Creating timing netlist..
  // Timing estimate: 0.24 ns (4161.98 MHz)
  ================================== [SUCCESS] Took 1.10 seconds ==============================

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

.. Executing: scons -Q time fpga_type=hx fpga_pack=tq144 fpga_size=1k -f /path/to/SConstruct
