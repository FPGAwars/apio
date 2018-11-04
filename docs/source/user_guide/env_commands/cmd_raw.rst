.. _cmd_raw:

apio raw
========

.. contents::

Usage
-----

.. code::

    apio raw '[CMD]'
    apio raw "[CMD]"

Description
-----------

Execute commands using Apio packages.

Argument
--------

.. program:: apio raw

.. option::
    cmd

Command to be executed using installed Apio packages.

Examples
--------

1. Run yosys (package installed with Apio)

.. code::

  $ apio raw 'yosys'

2. Generate a verilog diagram with yosys

.. code::

  $ apio raw 'yosys -p "read_verilog leds.v; show" -q'

.. image:: ../../../resources/images/yosys-show.png
