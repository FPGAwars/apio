# Using Custom Boards

Apio uses definitions of FPGA devices, FPGA programmers, and
FPGA boards to simplify the setup of new projects. The diagram below
illustrates the relationship between these definitions and Apio's operation,
as well as the names of their respective definition files in the apio 
`definitions` packages

<br>

![](assets/custom-boards.svg)

<br>

If any of these default definitions do not match the FPGA board you are using,
you can override them by placing custom definition files in the top-level
directory of your project. These replacement files should:

- Use the same file names and formats as the originals (`fpgas.jsonc`,
  `programmers.jsonc`, or `boards.jsonc`).
- Include only the specific FPGA, programmer, or board definitions you need.

## Definition Files

| Definition File       | Contains               | Keyed By        |
| :------------------ | :--------------------- | :-------------- |
| `fpgas.jsonc`       | FPGA definitions       | `fpga-id`       |
| `programmers.jsonc` | Programmer definitions | `programmer-id` |
| `boards.jsonc`      | Board definitions      | `board-id`      |

> If you believe your custom definition may be useful to others,
> consider submitting a pull request to the [apio-definitions](https://github.com/FPGAwars/apio-definitions/tree/main/definitions) repository.

## Example: Custom `boards.jsonc`

The following is an example of a custom `boards.jsonc` file that defines
a variant of the `upduino31` board:

```json
{
  "upduino31c": {
    "name": "UPduino v3.1c",
    "fpga-id": "ice40up5k-sg48",
    "programmer": {
      "id": "iceprog"
    },
    "usb": {
      "vid": "0403",
      "pid": "6010",
      "product-regex": "UPduino v3\\.1c"
    }
  }
}
```
