# Apio devices

---

## apio devices

The `apio devices` command group scans and displays devices connected to your
computer. It is mainly used for diagnosing connectivity or driver issues.

<h3>Options</h3>

```
-h, --help  Show this message and exit.
```

<h3>Subcommands</h3>

```
apio devices scan-usb
apio devices scan-serial
```

---

## apio devices scan-usb

The command `apio devices scan-usb` scans and displays the USB devices 
currently connected to your computer. It is useful for diagnosing FPGA board
connectivity issues.

<h3>Examples</h3>

```
apio devices scan-usb    # Lists USB devices.
```

<h3>Options</h3>

```
-h, --help  Show this message and exit.
```

Example output

![](assets/apio-devices-scanusb.png)

---

## apio devices scan-serial

The command `apio devices scan-serial` scans and displays the serial devices
currently connected to your computer. It is useful for diagnosing FPGA
board connectivity issues.

<h3>Examples</h3>

```
apio devices scan-serial    # List serial devices.
```

<h3>Options</h3>

```
-h, --help  Show this message and exit.
```

<h3>Notes</h3>

- Devices like the FTDI FT2232 with multiple channels may appear as
  multiple entries—one per serial port.

- On Windows, manufacturer and product strings of FTDI based devices may
  show their FTDI generic values rather than the custom values such as
  'Alhambra II' set by the device manufacturer.

Example output

![](assets/apio-devices-scanserial.png)
