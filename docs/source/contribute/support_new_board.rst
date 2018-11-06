.. support_new_board

Support a new board
===================

In order to support a new board based on FPGA Lattice iCE40 family, follow these steps:

1. **Find your FPGA name** in `fpgas.json <https://github.com/FPGAwars/apio/blob/develop/apio/resources/fpgas.json>`_. This file contains all FPGAs supported by the `Icestorm <http://www.clifford.at/icestorm>`_ project.

  .. code-block:: javascript

    "iCE40-HX1K-TQ144": {
      "type": "hx",
      "size": "1k",
      "pack": "tq144"
    }

  .. code-block:: javascript

    "iCE40-HX8K-CT256": {
      "type": "hx",
      "size": "8k",
      "pack": "ct256"
    }

  .. code-block:: javascript

    "iCE40-LP8K-CM81": {
      "type": "lp",
      "size": "8k",
      "pack": "cm81"
    }

2. **Find or add your programmer** in `programmers.json <https://github.com/FPGAwars/apio/blob/develop/apio/resources/programmers.json>`_.

  .. code-block:: javascript

    "iceprog": {
      "command": "iceprog",
      "args": "-d i:0x${VID}:0x${PID}:${FTDI_ID}"
    }

  .. code-block:: javascript

    "icoprog": {
      "command": "export WIRINGPI_GPIOMEM=1; icoprog",
      "args": "-p <"
    }

  .. code-block:: javascript

    "tinyprog": {
      "command": "tinyprog",
      "args": "--pyserial -c ${SERIAL_PORT} --program",
      "pip_packages": [ "tinyprog" ]
    }

  NOTE: if your programmer uses a python package, add this package and its version range to `distribution.json <https://github.com/FPGAwars/apio/blob/develop/apio/resources/distribution.json>`_.

  .. code-block:: javascript

    "pip_packages": {
      "blackiceprog": ">=2.0.0,<3.0.0",
      "litterbox": ">=0.2.1,<0.3.0",
      "tinyfpgab": ">=1.1.0,<1.2.0",
      "tinyprog": ">=1.0.21,<1.1.0"
    }

3. **Add your board** to `boards.json <https://github.com/FPGAwars/apio/blob/develop/apio/resources/boards.json>`_ with the following format:

  .. code-block:: javascript

    "icezum": {
      "name": "IceZUM Alhambra",
      "fpga": "iCE40-HX1K-TQ144",
      "programmer": {
        "type": "iceprog"
      },
      "usb": {
        "vid": "0403",
        "pid": "6010"
      },
      "ftdi": {
        "desc": "IceZUM Alhambra.*"
      }
    }

  .. code-block:: javascript

    "icoboard": {
      "name": "icoBOARD 1.0",
      "fpga": "iCE40-HX8K-CT256",
      "programmer": {
        "type": "icoprog"
      },
      "platform": "linux_armv7l"
    }

  .. code-block:: javascript

    "TinyFPGA-BX": {
      "name": "TinyFPGA BX",
      "fpga": "iCE40-LP8K-CM81",
      "programmer": {
        "type": "tinyprog"
      },
      "usb": {
        "vid": "1d50",
        "pid": "6130"
      },
      "tinyprog": {
        "desc": "TinyFPGA BX"
      }
    }
