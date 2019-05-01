.. user_guide

User Guide
==========

.. contents::

Project Structure
-----------------

An Apio project consist of the following files:

- The :ref:`apio_ini`. This is generated using :ref:`cmd_init`.
- A ``.pcf`` file. There should be exactly one PCF file per Apio project.
  The first PCF file that is found will be used for mapping wires to the physical FPGA pins for :ref:`cmd_build`.
- Verilog source files. All files ending in ``.v`` will be selected and included in the project automatically.
  If you don't want to include a Verilog file automatically, name it as ``.vh`` (Verilog Header) to exclude it.
  If you are using multiple files or including headers above your top module, mark the top module like so:

  .. code-block:: verilog

         (* top *)
         module my_top_module(
                 output led_r,
                 input serial_rxd,
         );
           ....
         endmodule

- Optionally, a testbench file ending in ``_tb.v``. This file will be excluded by :ref:`cmd_build`,
  but become the main module for :ref:`cmd_sim`.

Usage
-----

.. code-block:: bash

    apio [OPTIONS] COMMAND [ARGS]

You can execute just `apio` to see the help:

.. code-block:: none

  $ apio
  Usage: apio [OPTIONS] COMMAND [ARGS]...

  Options:
    --version  Show the version and exit.
    --help     Show this message and exit.

  Project commands:
    build      Synthesize the bitstream.
    clean      Clean the previous generated files.
    lint       Lint the verilog code.
    sim        Launch the verilog simulation.
    time       Bitstream timing analysis.
    upload     Upload the bitstream to the FPGA.
    verify     Verify the verilog code.

  Setup commands:
    drivers    Manage FPGA boards drivers.
    init       Manage apio projects.
    install    Install packages.
    uninstall  Uninstall packages.

  Utility commands:
    boards     Manage FPGA boards.
    config     Apio configuration.
    examples   Manage verilog examples.
    raw        Execute commands using Apio packages.
    system     System tools.
    upgrade    Check the latest Apio version.

Options
-------

.. program:: apio

.. option::
    --version

Show the version of Apio.

Project Commands
----------------

.. toctree::
    :maxdepth: 1

    project_commands/cmd_build
    project_commands/cmd_clean
    project_commands/cmd_lint
    project_commands/cmd_sim
    project_commands/cmd_time
    project_commands/cmd_upload
    project_commands/cmd_verify

Setup Commands
--------------

.. toctree::
    :maxdepth: 1

    setup_commands/cmd_drivers
    setup_commands/cmd_init
    setup_commands/cmd_install
    setup_commands/cmd_uninstall

Utility Commands
----------------

.. toctree::
    :maxdepth: 1

    util_commands/cmd_boards
    util_commands/cmd_config
    util_commands/cmd_examples
    util_commands/cmd_raw
    util_commands/cmd_system
    util_commands/cmd_upgrade

.. _apio_ini:

Project Configuration File (apio.ini)
------------------------------------

The ``apio.ini`` configuration file stores the Apio configuration for each project.
The current configuration parameters are:

=======  =========  ===========
Section  Parameter  Description
=======  =========  ===========
``env``  ``board``  the board, chosen from the list of :ref:`cmd_boards`.
=======  =========  ===========
