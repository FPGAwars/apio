# Listing Connected Devices

The `apio devices` command group lists devices connected to your computer.
It is mainly used for diagnosing connectivity or driver issues.

## OPTIONS

```
-h, --help  Show this message and exit.
```

## SUBCOMMANDS

```
apio devices usb
apio devices serial
```

---

# Apio devices usb

The command `apio devices usb` displays the USB devices currently
connected to your computer. It is useful for diagnosing FPGA board
connectivity issues.

## EXAMPLES

```
apio devices usb    # List USB devices.
```

## OPTIONS

```
-h, --help  Show this message and exit.
```

Example output

![](assets/apio-devices-usb.png)

---

# Listing devices serial

The command `apio devices serial` displays the serial devices
currently connected to your computer. It is useful for diagnosing FPGA
board connectivity issues.

## EXAMPLES

```
apio devices serial    # List serial devices.
```

## OPTIONS

```
-h, --help  Show this message and exit.
```

## NOTES

- Devices like the FTDI FT2232 with multiple channels may appear as
  multiple entries—one per serial port.

- On Windows, manufacturer and product strings of FTDI based devices may
  show their FTDI generic values rather than the custom values such as 'Alhambra II' set by the device manufacturer.

Example output

![](assets/apio-devices-serial.png)
