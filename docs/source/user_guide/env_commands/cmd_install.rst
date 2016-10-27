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
examples_   apio install examples   Verilog basic examples, pinouts, etc
gtkwave_    apio install gtkwave    Simulation viewer. `GTKWave project <http://gtkwave.sourceforge.net>`_ (only for Windows)
icestorm_   apio install icestorm   iCE40 FPGA synthesis, place & route and configuration tools. `Icestorm project <http://www.clifford.at/icestorm>`_
iverilog_   apio install iverilog   Verilog simulation and synthesis tool. `Icarus Verilog project <http://iverilog.icarus.com>`_
scons_      apio install scons      A software construction tool. `Scons project <http://scons.org>`_
system_     apio install system     Tools for listing the USB devices and retrieving information from the FTDI chips
==========  ======================  ============

.. _examples: https://github.com/FPGAwars/apio-examples
.. _gtkwave: https://github.com/FPGAwars/tool-gtkwave
.. _icestorm: https://github.com/FPGAwars/toolchain-icestorm
.. _iverilog: https://github.com/FPGAwars/toolchain-iverilog
.. _scons: https://github.com/FPGAwars/tool-scons
.. _system: https://github.com/FPGAwars/tools-system

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
  Download tools-system-linux_x86_64-1.0.0.tar.gz
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'system' has been successfully installed!
  Installing scons package:
  Download scons-2.4.1.tar.gz
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'scons' has been successfully installed!

2. Install ``examples`` package version 0.0.8

.. code::

  $ apio install examples@0.0.8
  Installing examples package:
  Download apio-examples-0.0.8.zip
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
  examples    Verilog examples               0.0.8
  scons       Scons tool                     2.4.1
  system      System tools                   1.0.0

  Not installed packages:

  -----------------------------------------------------------------------------
  Name        Description
  -----------------------------------------------------------------------------
  icestorm    Icestorm toolchain
  iverilog    Icarus Verilog toolchain

4. Install and update all packages

.. code::

  $ apio install --all
  Installing examples package:
  Already installed. Version 0.0.8
  Installing icestorm package:
  Download toolchain-icestorm-linux_x86_64-9.tar.gz
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'icestorm' has been successfully installed!
  Installing iverilog package:
  Download toolchain-iverilog-linux_x86_64-1.0.0.tar.gz
  Downloading  [####################################]  100%
  Unpacking  [####################################]  100%
  Package 'iverilog' has been successfully installed!
  Installing scons package:
  Already installed. Version 2.4.1
  Installing system package:
  Already installed. Version 1.0.0
