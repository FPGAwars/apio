.. _cmd_install:

apio install
============

.. contents::

Usage
-----

.. code::

    apio install [OPTIONS]

Description
-----------

Install packages. Automatically installs the latest version of the package. Also other versions can be installed using the following notation: **pacakge@version**.

Available packages

==========  ======================  ============
Package     Installation            Description
==========  ======================  ============
drivers_    apio install drivers    Drivers tools (only for Windows)
examples_   apio install examples   Verilog basic examples, pinouts, etc
gtkwave_    apio install gtkwave    Simulation viewer. `GTKWave project <http://gtkwave.sourceforge.net>`_ (only for Windows)
icestorm_   apio install icestorm   iCE40 FPGA synthesis, place & route and configuration tools. `Icestorm project <http://www.clifford.at/icestorm>`_
iverilog_   apio install iverilog   Verilog simulation and synthesis tool. `Icarus Verilog project <http://iverilog.icarus.com>`_
scons_      apio install scons      A software construction tool. `Scons project <http://scons.org>`_
system_     apio install system     Tools for listing the USB devices and retrieving information from the FTDI chips
verilator_  apio install verilator  Verilog HDL simulator. `Verilator project <https://www.veripool.org/wiki/verilator>`_
==========  ======================  ============

.. _drivers: https://github.com/FPGAwars/tools-drivers
.. _examples: https://github.com/FPGAwars/apio-examples
.. _gtkwave: https://github.com/FPGAwars/tool-gtkwave
.. _icestorm: https://github.com/FPGAwars/toolchain-icestorm
.. _iverilog: https://github.com/FPGAwars/toolchain-iverilog
.. _scons: https://github.com/FPGAwars/tool-scons
.. _system: https://github.com/FPGAwars/tools-system
.. _verilator: https://github.com/FPGAwars/toolchain-verilator

Options
-------

.. program:: apio install

.. option::
    -a, --all

Install all packages.

.. option::
    -l, --list

List all available packages.

.. option::
    -f, --force

Force the packages installation.

.. option::
    -p, --platform

    Set the platform [linux, linux_x86_64, linux_i686, linux_armv7l, linux_aarch64, windows, windows_amd64, windows_x86, darwin] (Advanced).

Examples
--------

1. Install ``system`` and ``icestorm`` packages:

.. code::

  $ apio install system icestorm
  Installing system package:
  Download tools-system-linux_x86_64-1.1.0.tar.gz
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'system' has been successfully installed!
  Installing icestorm package:
  Download toolchain-icestorm-linux_x86_64-1.11.0.tar.gz
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'icestorm' has been successfully installed!

2. Install ``examples`` package version 0.0.11

.. code::

  $ apio install examples@0.0.11
  Installing examples package:
  Download apio-examples-0.0.11.zip
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'examples' has been successfully installed!

3. Show all available packages

.. code::

  $ apio install --list

  Installed packages:

  -----------------------------------------------------------------------------
  Name        Description                    Version
  -----------------------------------------------------------------------------
  examples    Verilog examples               0.0.11
  icestorm    Icestorm toolchain             1.11.0
  system      System tools                   1.1.0

  Not installed packages:

  -----------------------------------------------------------------------------
  Name        Description
  -----------------------------------------------------------------------------
  iverilog    Icarus Verilog toolchain
  scons       Scons tool
  verilator   Verilator toolchain

4. Install and update all packages

.. code::

  $ apio install --all
  Installing examples package:
  Already installed. Version 0.0.11
  Installing icestorm package:
  Already installed. Version 1.11.0
  Installing iverilog package:
  Download toolchain-iverilog-linux_x86_64-1.2.0.tar.gz
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'iverilog' has been successfully installed!
  Installing scons package:
  Download scons-3.0.1.tar.gz
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'scons' has been successfully installed!
  Installing system package:
  Already installed. Version 1.1.0
  Installing verilator package:
  Download toolchain-verilator-linux_x86_64-1.0.0.tar.gz
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'verilator' has been successfully installed!

5. Install the ``drivers`` package for **windows** in a linux platform

.. code::

  $ apio install drivers --platform windows
  Installing drivers package:
  Download tools-drivers-windows-1.1.0.tar.gz
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'drivers' has been successfully installed!
