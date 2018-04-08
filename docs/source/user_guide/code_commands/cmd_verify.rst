.. _cmd_verify:

apio verify
===========

.. contents::

Usage
-----

.. code::

    apio verify [OPTIONS]

Description
-----------

Verify the **verilog** code. It is agnostic of the FPGA. It does not use the *pcf* file.

Required packages: ``scons``, ``iverilog``.

Options
-------

.. option::
    -p, --project-dir

Set the target directory for the project.

Examples
--------


1. Verify the *leds example*

.. code::

  $ apio verify
  iverilog -B /path/to/lib/ivl -o hardware.out -D VCD_OUTPUT= /path/to/vlib/system.v leds.v
  ================================== [SUCCESS] Took 0.17 seconds ==============================

..  Executing: scons -Q verify -f /path/to/SConstruct
