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

.. program:: apio uninstall

.. option::
    -a, --all

Uninstall all packages

.. option::
    -l, --list

List all installed packages

Examples
--------

1. Uninstall ``examples`` package

.. code::

  $ apio uninstall examples
  Do you want to continue? [y/N]: y
  Uninstalling examples package
  Package 'examples' has been successfully uninstalled!
