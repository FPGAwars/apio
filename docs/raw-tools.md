# Raw tools

The `apio raw` command provides access to additional tools that are included
in the apio packages, for example, in the `oss-cad-suite` package from the
YosysHQ project.

This page describes several such raw tools that are available in Apio. This list is not exhaustive.

> If you encounter a useful tool in the apio packages that is not listed
> here please please file an issue in the
> [Apio repository](https://github.com/fpgawars/apio/issues) to add it.

---

## ICE40 PLL generator

The ICE40 PLL Generator is a command-line tool that creates an ICE40 PLL module from specified flags. It is used to run the design at a different, typically higher, frequency than that of the external clock.

Get help text.

```
apio raw -- icepll -h
```

Generate a PLL module that converts a 12 MHz input to a 48 MHz output clock.

```
apio raw -- icepll -i 12 -o 48 -m -f pll.v
apio format pll.v
```

The Apio example `alhambra/pll` demonstrates a `pll.v` module that
was generated with this command.

> Per [Apio issue 669](https://github.com/FPGAwars/apio/issues/669),
> the generated module does not pass `apio lint` because it
> doesn't specify the unused PLL signals. As a workaround, manually add the following
> signals to the PLL instantiation in `pll.v`:

```
.PLLOUTGLOBAL(),
.EXTFEEDBACK(),
.LATCHINPUTVALUE(),
.SDO(),
.SDI(),
.SCLK(),
.DYNAMICDELAY()
```

---

## ECP5 PLL generator

The ECP5 PLL Generator is a command-line tool that creates an ECP5 PLL module from specified flags. It is used to run the design at a different, typically higher, frequency than that of the external clock.

Get help text.

```
apio raw -- ecppll -h
```

Generate a PLL module that converts a 25 MHz input to a 120 MHz output clock.

```
apio raw -- ecppll -i 25 -o 120 -f pll.v
apio format pll.v
```

The Apio example `colorlight-5a-75b-v8/pll` demonstrates a `pll.v` module that
was generated with this command.

> Per [Apio issue 670](https://github.com/FPGAwars/apio/issues/669),
> the generated module does not pass `apio lint` because it
> doesn't specify the unused PLL signals. As a workaround, manually add the following
> signals to the PLL instantiation in `pll.v`:

```
.ENCLKOS(),
.ENCLKOS2(),
.ENCLKOS3(),
.CLKOS(),
.CLKOS2(),
.CLKOS3(),
.INTLOCK(),
.REFCLK()
```

---

## Gowin PLL generator

The GOWIN PLL Generator is a command-line tool that creates a GOWIN PLL module from specified flags. It is used to run the design at a different, typically higher, frequency than that of the external clock.

Get help text.

```
apio raw -- gowin_pll -h
```

Generate a PLL module for the Sipeed Nano 9K that converts a 27 MHz input to a 75 MHz output clock.

```
apio raw -- gowin_pll -d "GW1NR-LV9QN88PC6/I5" -i 27 -o 75 -f pll.v
apio format pll.v
```

The Apio example `sipeed-tang-nano-9k/pll` demonstrates a `pll.v` module that
was generated with this command.

> The value of the `-d` option is the `part-num` value from the output of the
> command `apio api get-project`. For example, for the Tang Nano 20k board,
> the value is `GW2AR-LV18QN88C8/I7`.

---

## Xilinx 7-series PLL generator

The Xilinx 7-series PLL Generator is a command-line tool that creates a
Xilinx 7-series PLL module (`PLLE2_BASE`) from specified flags. It is used
to run the design at a different, typically higher, frequency than that of
the external clock. The tool is included in the `openxc7` package.

Get help text.

```
apio raw -- xc7pll -h
```

Generate a PLL module that converts a 100 MHz input to a 200 MHz output clock.

```
apio raw -- xc7pll -i 100 -o 200 -m -f pll.v
apio format pll.v
```

> The `-o` option can be repeated to generate up to six output clocks from
> a single PLL, for example `xc7pll -i 100 -o 100 -o 200 -m -f pll.v`.
> When a requested frequency cannot be synthesized exactly, the tool picks
> the closest achievable value and reports the deviation; run it without
> `-m` to see the frequency report. Output frequencies must be within the
> PLL range of 6.25 to 1600 MHz.

> The generated module specifies all PLL signals, including the unused
> ones, and passes `apio lint` as is.

---

## Zadig (Windows only)

Zadig is a third party Windows tool that allow to manage and replace USB
device drivers. Zadig is used by Apio to install and uninstall FPGA boards
drivers on windows but can also be used independently using the command

```
apio raw -- zadig
```

---

## Verible verilog diff

verible verilog diff is a command line tool that finds the semantic differences
between verilog files.

Get help text.

```
apio raw -- verible-verilog-diff --helpfull
```
