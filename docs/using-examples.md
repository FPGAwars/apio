# Using Apio's Examples

Apio comes with a set of sample projects that demonstrate its features and can be used as starting points for your own projects. To list the available examples, type:

```
$ apio examples list
```

```
┌────────────────────────────────┬───────┬─────────────────────────────────────────────────────────────┐
│ BOARD/EXAMPLE                  │ ARCH  │ DESCRIPTION                                                 │
├────────────────────────────────┼───────┼─────────────────────────────────────────────────────────────┤
│ alchitry-cu/blinky             │ ice40 │ Blinking all LEDs                                           │
│ alhambra-ii/bcd-counter        │ ice40 │ Verilog example with testbenches and subdirectories.        │
│ alhambra-ii/bcd-counter-sv     │ ice40 │ SystemVerilog example with testbenches and subdirectories.  │
│ alhambra-ii/blinky             │ ice40 │ Blinking LED                                                │
│ alhambra-ii/getting-started    │ ice40 │ Example for Apio Getting Started docs.                      │
│ alhambra-ii/ledon              │ ice40 │ Turning on an LED                                           │
│ sipeed-tang-nano-9k/blinky-sv  │ gowin │ Blinking LED (SystemVerilog)                                │
│ sipeed-tang-nano-9k/pll        │ gowin │ PLL clock multiplier                                        │
└────────────────────────────────┴───────┴─────────────────────────────────────────────────────────────┘
```

To fetch an example we create a new empty directory and fetch the example files int it.

```
# Create an empty project directory
$ apio mkdir work
$ cd work

# Fetch the example
$ apio example fetch alhambra-ii/getting-started
```

Now lets look at the project file structure

```
$ tree .
.
├── apio.ini
├── main_tb.gtkw
├── main_tb.v
├── main.v
└── pinout.pcf
```

And the project file `apio.ini`.
```
$ cat -n apio.ini
     1  ; Apio project file.
     2
     3  [env:default]
     4
     5  ; Board ID
     6  board = alhambra-ii
     7
     8  ; Top module name (in main.v)
     9  top-module = Main
```

The fetched example is now an Apio project that can be built and uploaded to a matching FPGA board.
