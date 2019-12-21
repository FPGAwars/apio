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

Required packages: ``scons``.

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
  Removed hardware.blif
  Removed hardware.asc
  Removed hardware.bin
  Removed hardware.out
  ================================== [SUCCESS] Took 0.17 seconds ==============================

.. Executing: scons -Q -c -f /path/to/SConstruct
