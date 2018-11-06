.. _cmd_uninstall:

apio uninstall
==============

.. contents::

Usage
-----

.. code::

    apio uninstall [OPTIONS]

Description
-----------

Uninstall packages. Before uninstalling a package, a confirmation is requested.

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

.. program:: apio uninstall

.. option::
    -a, --all

Uninstall all packages.

.. option::
    -l, --list

List all installed packages.

.. option::
    -p, --platform

    Set the platform [linux_x86_64, linux_i686, linux_armv7l, linux_aarch64, windows, darwin] (Advanced).

Examples
--------

1. Uninstall ``examples`` package

.. code::

  $ apio uninstall examples
  Do you want to continue? [y/N]: y
  Uninstalling examples package:
  Package 'examples' has been successfully uninstalled!

2. Uninstall the ``drivers`` package for **windows** in a linux platform

.. code::

  $ apio uninstall drivers --platform windows
  Do you want to continue? [y/N]: y
  Uninstalling drivers package:
  Package 'drivers' has been successfully uninstalled!
