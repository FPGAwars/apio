# FPGA Board Drivers

Some FPGA boards require a system driver before the programmer can access them. When this is the case, install the driver with the `apio drivers install` command.

Apio provides two types of driver: `ftdi` and `serial`. The table below compares them.

> - Driver installation is not required on macOS.

> - If the FPGA board appears in the device list with `--unavail--` manufacturer or product strings, the appropriate driver probably needs to be installed.

|                  | FTDI driver                   | Serial driver                   |
| ---------------- | :---------------------------- | :------------------------------ |
| Platforms        | Linux, Windows                | Linux, Windows                  |
| Driver install   | `apio drivers install ftdi`   | `apio drivers install serial`   |
| Driver uninstall | `apio drivers uninstall ftdi` | `apio drivers uninstall serial` |
| List devices     | `apio devices usb`            | `apio devices serial`           |
