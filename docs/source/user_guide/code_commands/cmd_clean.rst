.. _cmd_clean:

apio clean
==========

.. contents::

Usage
-----

.. code::

    apio clean [OPTIONS]

Description
-----------

Clean the previous generated files: **blif**, **asc**, **bin**, **rpt** and **out**.

This command requires the ``scons`` package.

Options
-------

.. option::
    -p, --project-dir

Set the target directory for the project.

Examples
--------

1. Clean the *leds example*

.. code::

  $ apio clean
  Using default SConstruct file
  Removed hardware.blif
  Removed hardware.asc
  Removed hardware.bin
  Removed hardware.out
  ================================== [SUCCESS] Took 0.17 seconds =================================

.. Executing: scons -Q -c -f /path/to/SConstruct
