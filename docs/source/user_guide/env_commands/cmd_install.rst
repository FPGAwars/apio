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
icestorm_   apio install icestorm   iCE40 FPGA synthesis, place & route and configuration tools. `Icestorm project <http://www.clifford.at/icestorm>`_
iverilog_   apio install iverilog   Verilog simulation and synthesis tool. `Icarus Verilog project <http://iverilog.icarus.com/>`_
scons_      apio install scons      A software construction tool. `Scons project <http://scons.org/>`_
system_     apio install system     Tools for listing the USB devices and retrieving information from the FTDI chips
examples_   apio install examples   Verilog basic examples, pinouts, etc
pio-fpga_   apio install pio-fpga   PlatformIO experimental configuration for supporting Lattice FPGA boards
==========  ======================  ============

.. _icestorm: https://github.com/FPGAwars/toolchain-icestorm
.. _iverilog: https://github.com/FPGAwars/toolchain-iverilog
.. _scons: https://github.com/FPGAwars/tool-scons
.. _system: https://github.com/FPGAwars/tools-usb-ftdi
.. _examples: https://github.com/FPGAwars/apio-examples
.. _pio-fpga: https://github.com/FPGAwars/Platformio-FPGA

Options
-------

.. program:: apio install

.. option::
    -a, --all

Install all packages

.. option::
    -l, --list

List all available packages


Examples
--------

1. Install ``system`` and ``scons`` packages:

.. code::

  $ apio install system scons
  Installing system package:
  Download tools-usb-ftdi-linux_x86_64-1.tar.bz2
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'system' has been successfully installed!
  Installing scons package:
  Download scons-2.4.1.tar.gz
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'scons' has been successfully installed!

2. Install ``examples`` package version 0.0.2

.. code::

  $ apio install examples@0.0.2
  Installing examples package:
  Download apio-examples-0.0.2.zip
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
  system      System development tools       1
  scons       Scons toolchain                2.4.1
  examples    Verilog examples               0.0.2

  Not installed packages:

  -----------------------------------------------------------------------------
  Name        Description
  -----------------------------------------------------------------------------
  icestorm    Icestorm toolchain
  pio-fpga    Platformio-fpga support
  iverilog    Icarus Verilog toolchain

4. Install and update all packages

.. code::

  $ apio install --all
  Installing icestorm package:
  Download toolchain-icestorm-linux_x86_64-9.tar.gz
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'icestorm' has been successfully installed!
  Installing system package:
  Already installed. Version 1
  Installing iverilog package:
  Download toolchain-iverilog-linux_x86_64-3.tar.bz2
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'iverilog' has been successfully installed!
  Installing scons package:
  Already installed. Version 2.4.1
  Installing examples package:
  Download apio-examples-0.0.3.zip
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'examples' has been successfully installed!
