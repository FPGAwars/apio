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

[TODO table]
* examples
* icestorm
* iverilog
* scons
* system

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
