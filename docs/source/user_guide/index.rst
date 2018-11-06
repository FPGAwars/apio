.. user_guide

User Guide
==========

.. contents::

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
