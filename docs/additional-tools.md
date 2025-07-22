# Additional tools

The `apio raw` command provides access to additional tools that are included
in the apio packages, for example, in the `oss-cad-suite` package from the
YosysHQ project.

This page describes several additional tools available in Apio. The list is not exhaustive.

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
apio raw -- icepll -i 12 -o 48 -q -m -f pll.v
apio format pll.v
```

> The Apio example `alhambra/pll` demonstrates a complete project that uses
> an ICE40 PLL. The `pll.v` file in the example includes unused signal references added to satisfy `apio lint`.
> This issue is tracked at <https://github.com/FPGAwars/apio/issues/669>.

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

> The Apio example `colorlight-5a-75b-v8/pll` demonstrates a complete project that uses
> an ECP5 PLL. The `pll.v` file in the example includes unused signal references added to satisfy `apio lint`.
> This issue is tracked at <https://github.com/FPGAwars/apio/issues/670>.

---

## Gowin PLL generator

The GOWIN PLL Generator is a command-line tool that creates a GOWIN PLL module from specified flags. It is used to run the design at a different, typically higher, frequency than that of the external clock.

Get help text.

```
apio raw -- gowin_pll -h
```

Generate a PLL module for the Sipeed Nano 9K that converts a 27 MHz input to a 75 MHz output clock.

```
apio raw -- gowin_pll -d "GW1NR-9 C6/I5" -i 27 -o 75 -f pll.v
apio format pll.v
```

> The Apio example `sipeed-tang-nano-9k/pll` demonstrates a complete project that uses
> an GOWIN PLL. The `pll.v` file of the example includes unused signal references added to satisfy `apio lint`.
> This is tracked in issue <>.

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


