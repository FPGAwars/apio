# Apio upload

The `apio upload` command builds the bitstream (like `apio build`) and uploads it to the FPGA board.

## EXAMPLES

```
apio upload                            # Typical usage
apio upload -s /dev/cu.usbserial-1300  # Specify serial port
apio upload -n FTXYA34Z                # Specify USB serial number
```

## OPTIONS

```
-s, --serial-port serial-port  Specify the serial port
-n, --serial-num serial-num    Specify the device's USB serial number
-e, --env name                 Use a named environment from apio.ini
-p, --project-dir path         Specify the project root directory
-h, --help                     Show this help message and exit
```

## NOTES

- In most cases, `apio upload` is enough to locate and program the FPGA board. Use the `--serial-port` or `--serial-num` options to select a specific board if multiple matching devices are connected.

- Use `apio devices` to list connected USB and serial devices, and `apio drivers` to install or uninstall device drivers.

- You can override the board's default programmer using the `programmer-cmd` option in `apio.ini`.
