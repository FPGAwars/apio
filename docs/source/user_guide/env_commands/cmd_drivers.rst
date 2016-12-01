.. _cmd_drivers:

apio drivers
============

.. contents::

Usage
-----

.. code::

    apio drivers [OPTIONS]

Description
-----------

Enable/Disable the FTDI drivers.

* Linux: add the rules file. It may require a reboot or to uplug and reconnect the board.
* Mac OSX: configure FTDIUSBSerialDriver and AppleUSBFTDI keys and install libftdi.
* Windows: open zadig to replace the current driver by libusbK. It requires to uplug and reconnect the board.

This command requires the ``driver`` package (only for Windows).

.. note::

  More information in :ref:`install_drivers`

Options
-------

.. program:: apio drivers

.. option::
    -e, --enable

Enable FPGA drivers

.. option::
    -d, --disable

Disable FPGA drivers

Examples
--------

1. Enable the FTDI drivers on Linux

.. code::

  $ apio drivers --enable
  Configure FTDI drivers for FPGA
  [sudo] password for user:
  FPGA drivers enabled

1. Disable the FTDI drivers on Linux

.. code::

  $ apio drivers --disable
  Revert FTDI drivers configuration
  [sudo] password for user:
  FPGA drivers disabled
