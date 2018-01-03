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
    --ftdi-enable

Enable FPGA drivers.

.. option::
    --ftdi-disable

Disable FPGA drivers.

.. option::
    --serial-enable

Enable Serial drivers.

.. option::
    --serial-disable

Disable Serial drivers.


Examples
--------

1. Enable the FTDI drivers on Linux

.. code::

  $ apio drivers --ftdi-enable
  Configure FTDI drivers for FPGA
  [sudo] password for user:
  FTDI drivers enabled
  Unplug and reconnect your board

2. Disable the FTDI drivers on Linux

.. code::

  $ apio drivers --ftdi-disable
  Revert FTDI drivers configuration
  [sudo] password for user:
  FTDI drivers disabled
  Unplug and reconnect your board


3. Enable the Serial drivers on Linux

.. code::

  $ apio drivers --serial-enable
  Configure Serial drivers for FPGA
  [sudo] password for user:
  Serial drivers enabled
  Unplug and reconnect your board

4. Disable the Serial drivers on Linux

.. code::

  $ apio drivers --serial-disable
  Revert Serial drivers configuration
  [sudo] password for user:
  Serial drivers disabled
  Unplug and reconnect your board
