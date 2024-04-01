.. user_guide

User Guide
==========

.. contents::

Project Structure
-----------------

An Apio project consist of the following files:

- The :ref:`apio_ini`. This is generated using :ref:`cmd_init`.
- A ``.pcf`` file. There should be exactly one PCF file per Apio project.
  The first PCF file that is found will be used for mapping wires to the physical FPGA pins for :ref:`cmd_build`.
- Verilog source files. All files ending in ``.v`` will be selected and included in the project automatically.
  If you don't want to include a Verilog file automatically, name it as ``.vh`` (Verilog Header) to exclude it.
  If you are using multiple files or including headers above your top module, mark the top module like so:

  .. code-block:: verilog

         (* top *)
         module my_top_module(
                 output led_r,
                 input serial_rxd,
         );
           ....
         endmodule

- Optionally, a testbench file ending in ``_tb.v``. This file will be excluded by :ref:`cmd_build`,
  but become the main module for :ref:`cmd_sim`.

.. _apio_ini:

Project Configuration File (apio.ini)
------------------------------------

The ``apio.ini`` configuration file stores the Apio configuration for each project.
The current configuration parameters are:

=======  =========  ===========
Section  Parameter  Description
=======  =========  ===========
``env``  ``board``  the board, chosen from the list of :ref:`cmd_boards`.
=======  =========  ===========
