.. _cmd_lint:

apio lint
=========

.. contents::

Usage
-----

.. code::

    apio lint [OPTIONS]

Description
-----------

Lint the **verilog** code. It is agnostic of the FPGA. It does not use the *pcf* file.

Required packages: ``scons``, ``verilator``.

Options
-------

.. option::
    -a, --all

.. option::
    -p, --project-dir

Set the target directory for the project.

Examples
--------


1. Lint the *leds example*

.. code::

  $ apio lint
  verilator --lint-only -I/path/to/share leds.v
  ================================== [SUCCESS] Took 0.20 seconds ==============================

..  Executing: scons -Q lint -f /path/to/SConstruct
