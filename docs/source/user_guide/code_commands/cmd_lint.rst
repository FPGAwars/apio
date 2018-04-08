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

Enable all warnings, including code style warnings.

.. option::
    -t, --top

Set top module.

.. option::
    --nostyle

Disable all style warnings.

.. option::
    --nowarn

Disable specific warning(s).

.. option::
    --warn

Enable specific warning(s).

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

2. Lint the *leds example* with all the options

.. code::

  $ apio lint --all --top leds --nostyle --nowarn PINMISSING,WIDTH --warn DECLFILENAME,DEFPARAM
  verilator --lint-only -I/path/to/share -Wall -Wno-style -Wno-PINMISSING -Wno-WIDTH -Wwarn-DECLFILENAME -Wwarn-DEFPARAM --top-module leds leds.v
  ================================== [SUCCESS] Took 0.20 seconds ==============================

..  Executing:Executing: scons -Q lint warn=DECLFILENAME,DEFPARAM all=True nowarn=PINMISSING,WIDTH top=leds nostyle=True -f /path/to/SConstruct
