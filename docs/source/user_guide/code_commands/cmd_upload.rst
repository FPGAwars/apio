.. _cmd_upload:

apio upload
===========

.. contents::

Usage
-----

.. code::

    apio upload [OPTIONS]

Description
-----------

Upload the bitstream to the FPGA. It builds the project if required.

It also performs an automatic discovery and validation of the FTDI chip depending on the selected board.

This command requires the ``system``, ``scons`` and ``icestorm`` packages.

.. note::

  FTDI driver configuration must be done before upload. More information in :ref:`cmd_drivers`.

Options
-------

.. program:: apio upload

.. option::
    -d, --device

Select a specific device index. This numerical index is provided by **libftdi1**, that is different from *libftdi0*.

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

.. note::

  All available boards, FPGAs, sizes, types and packs are showed in :ref:`cmd_boards`

Examples
--------

1. Upload the *leds example*

.. code::

  $ apio upload
  Info: use apio.ini board: icezum
  Number of FTDI devices found: 1
  Checking device: 0
  Manufacturer: Mareldem, Description: IceZUM Alhambra v1.1 - B01-020

  Using default SConstruct file
  [] Processing icezum
  -------------------------------------------------------------------------------------------------
  FPGA_SIZE: 1k
  FPGA_TYPE: hx
  FPGA_PACK: tq144
  DEVICE: 0
  iceprog -d i:0x0403:0x6010:0 hardware.bin
  init..
  cdone: high
  reset..
  cdone: low
  flash ID: 0x20 0xBA 0x16 0x10 0x00 0x00 0x23 0x51 0x85 0x32 0x13 0x00 0x54 0x00 0x29 0x10 0x06 0x15 0x51 0x62
  file size: 32220
  erase 64kB sector at 0x000000..
  programming..
  reading..
  VERIFY OK
  cdone: high
  Bye.
  ================================== [SUCCESS] Took 1.96 seconds =================================

.. Executing: scons -Q upload fpga_type=hx fpga_pack=tq144 fpga_size=1k device=0 -f /path/to/SConstruct
