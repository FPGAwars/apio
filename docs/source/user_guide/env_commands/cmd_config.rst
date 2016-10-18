.. _cmd_config:

apio config
===========

.. contents::

Usage
-----

.. code::

    apio config [OPTIONS]

Description
-----------

Apio configuration commands.

Options
-------

.. program:: apio config

.. option::
    -l, --list

List all configuration parameters

.. option::
    -e, --exe [apio|native]

Configure executables: `apio` selects apio packages, `native` selects system binaries

Examples
--------

1. Show all configuration parameters

.. code::

  $ apio config --list
  Executable mode: apio

2. Enable native mode for executable binaries

.. code::

  $ apio config --exe native
  Executable mode updated: native
