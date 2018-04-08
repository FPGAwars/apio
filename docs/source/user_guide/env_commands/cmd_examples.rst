.. _cmd_examples:

apio examples
=============

.. contents::

Usage
-----

.. code::

    apio examples [OPTIONS]

Description
-----------

Manage verilog examples: https://github.com/FPGAwars/apio-examples

This command requires the ``examples`` package.

Options
-------

.. program:: apio examples

.. option::
    -l, --list

List all available examples.

.. option::
    -d, --dir

Copy the selected example directory.

.. option::
    -f, --files

Copy the selected example files.

.. option::
    -p, --project-dir

Set the target directory for the examples.

.. option::
    -n, --sayno

Automatically answer NO to all the questions.

Examples
--------

1. Show all available examples

.. code::

  $ apio examples --list
  [ ... ]

  leds
  ---------------------------------------------------------------------------------------------
  Verilog example for Turning all the leds on (for the icestick/icezum boards)

  wire
  ---------------------------------------------------------------------------------------------
  Verilog example on how to describe a simple wire

  [ ...]

2. Copy the *leds example* files

.. code::

  $ apio examples --files leds
  Copying leds example files ...
  Example files 'leds' have been successfully created!

  $ ls
  leds.pcf  leds_tb.gtkw  leds_tb.v  leds.v

3. Copy the *leds example* directory

.. code::

  $ apio examples --dir leds
  Creating leds directory ...
  Example 'leds' has been successfully created!

  $ tree leds
  leds
  ├── info
  ├── leds.pcf
  ├── leds_tb.gtkw
  ├── leds_tb.v
  └── leds.v
