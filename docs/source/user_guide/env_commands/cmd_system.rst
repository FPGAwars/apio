.. _cmd_system:

apio system
===========

.. contents::

Usage
-----

.. code::

    apio system [OPTIONS]

Description
-----------

System tools: https://github.com/FPGAwars/tools-system

This command requires the ``system`` package.


Options
-------

.. program:: apio system

.. option::
    --lsftdi

List all connected FTDI devices.

.. option::
    --lsusb

List all connected USB devices.

.. option::
    --lsserial

List all connected Serial devices.

.. option::
    -i, --info

Show system information.

Examples
--------

1. List connected FTDI devices

.. code::

  $ apio system --lsftdi
  Number of FTDI devices found: 1
  Checking device: 0
  Manufacturer: Mareldem, Description: IceZUM Alhambra v1.1 - B01-020

2. List connected USB devices

.. code::

  $ apio system --lsusb
  1d6b:0003 (bus 3, device 1)
  04ca:7049 (bus 2, device 4) path: 8
  8087:0a2a (bus 2, device 3) path: 7
  138a:0017 (bus 2, device 2) path: 6
  0403:6010 (bus 2, device 69) path: 2
  1d6b:0002 (bus 2, device 1)
  8087:8001 (bus 1, device 2) path: 1
  1d6b:0002 (bus 1, device 1)

3. List connected Serial devices

.. code::

  $ apio system --lsserial
  Number of Serial devices found: 2

  /dev/ttyUSB1
  Description: IceZUM Alhambra v1.1 - B01-020
  Hardware info: USB VID:PID=0403:6010 LOCATION=2-2:1.1

  /dev/ttyUSB0
  Description: IceZUM Alhambra v1.1 - B01-020
  Hardware info: USB VID:PID=0403:6010 LOCATION=2-2:1.0

4. Show system information

.. code::

  $ apio system --info
  Platform: linux_x86_64
