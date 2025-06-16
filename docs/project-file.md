# The apio.ini project file

Every Apio project is required to have in its root directory a text
file named `apio.ini` that contains the project configuration. At
minimum, the file looks like the example below with a single `env`
section and the require configuration options.

```
[env:default]
board = alhambra-ii   ; Board id
top-module = Main     ; Top Verilog module name
```

Below is a more complex `apio.ini` file that contains two `[env:name]` sections named `env1` and `env2`, a `[common]` section with settings that are shared by all envs, and an `[apio]` section the selects the `env2` as the default env.

```
; Optional [apio] section.
[apio]
default-env = env2

; Optional [common] section.
[common]
board = alhambra-ii
top-module = Main

; Required first env section.
[env:env1]
default-testbench = main_tb.v

; Optional additional env section(s).
[env:env2]
default-testbench = io_module_tb.v
```

At runtime, apio select the env to use based using the following rules in decreasing priorities:

1. The value of the flag `--env`, if specified.
2. The value of the `default-env` option in the `[apio]` section, if exists.
3. The first env that is listed in `apio.ini`.

When apio determines the env to use, it collects its options
from the `[common]` and the [env:name] section, with options in the `[env:name]` section
having higher priority, and executes the command with the resolved set options.

---

## The \[apio] section

The `[apio]` section is optional and currently supports the following options

### The `default-env` option

This is an optional option that species the name of the default env. Without this option, the default option is the first one that is listed in `apio.ini`.

```
[apio]
default-env = env2
```

---

## The \[common\] section

The `[common]` section is optional and supports any option that is also supported by the `[env:name]` sections. Any option defined in the `[common]` section will be shared by all `[env:name]` sections that do not explicitly define that option.

---

## The \[env:name] sections

The `[env:name]` section defines a name build environment and every Apio project should include at least one
`[env:name]` section. For projects with a single env, it's common to call it `[env:default]`. Following is
the list of options that can appear in an `[env:name]` section and/or in the `[common]` section.

### The `board` option (REQUIRED)

The required `board` option specifies the ID of the board that is used in with this env.
The board ID must be one of the board IDs that are listed by the command `apio boards` (e.g. `alhambra-ii`).

```
[env:default]
board = alhambra-ii
```

Apio uses the board ID to determine information such as the FPGA part
number and the programmer command to use to upload the design to the
board.

If your project contains a `boards.jsonc` file with custom board defintion, the
board ID must be from that file.

### The `default-testbench` option

The optional `default-testbench` option is useful with Apio projects that contain more than one testbench and it allows to specify the testbench that `apio sim` should simulate by default if a no testbench is specified. The value of the option is the relative path
to the testbench file from the project root dir.

```
[env:default]
default-testbench = tests/main_tb.v
```

### The `defines` option

The optional `defines` option allows to specify Verilog macros that are passed
to verilog parsers such as Yosys and Iverilog.

Each macro is specified in a separate lines and the marcors are passed to the
Verilog parsers as `-D` command lines options. For example the marocs below
are passed as `-DDEBUG_MODE -D45`.

```
[env:default]
defines =
    DEBUG_MODE
    SPEED=45
```

In the following example, the `defines` option is use to select the blinking rate in a project with two envs.

```
; Env for build with fast blink.
[env:fast]
defines =
    CLK_DIV=3_000_000

; Env for build with slow blink.
[env:slow]
defines =
    CLK_DIV=12_000_000
```

### The `format-verible-options` option

The optional `format-verible-options` option allows to control the operation
of the `apio format` command by specifying additional options to the
underlying Verible formatter.

```
[env:default]
format-verible-options =
    --column_limit=80
    --indentation_spaces=4
```

For the list of the Verible formatter options, run the command `apio 
raw -- verible-verilog-format --helpfull`

### The `programmer-cmd` option

he optional `programmer-cmd` option allows to override the programmer command
used by the `apio upload` command. It is intended for special cases and should be
avoided if possible.

```
[env:default]
 programmer-cmd = iceprog -d i:0x${VID}:0x${PID} ${BIN_FILE}
```

> The list of supported placeholders is available in the Apio
> standard boards definitions files `boards.jsonc`.

### The `top-module option` (REQUIRED)

The optional `top-module` option specifies the name of the top module of the
design.

```
[env:default]
top-module = Blinky
```

### The `yosys-synth-extra-options` option

The optional `yosys-synth-extra-options` option allows adding options to the
Yosys synth command used by the `apio build` command. In the example below, it adds the option `-dsp`,
which enables on some FPGAs the use of `DSP` cells to implement
multiply operations. This is an advanced option that is
typically not needed.

```
[env:default]
yosys-synth-extra-options = -dsp
```
