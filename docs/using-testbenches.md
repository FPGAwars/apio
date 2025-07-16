# Using testbenches

Testbenches are non-synthesizable Verilog files with the suffix `_tb.v` and SystemVerilog files with the suffix `_tb.sv` that are used to simulate and test the synthesizable modules of the project. Testbenches are used by the command `apio sim` for simulation with a graphical view of the signals, and by `apio test` for a batch test to ensure that none of the assertions in the testbenches fail.

Testbench files can be placed anywhere in the project directory tree, either near the modules they test or in a separate directory dedicated to testing. When you run `apio sim` and view the results in GTKWave, it is recommended to save the GTKWave configuration in a `.gtkw` file named after its testbench so that it will take effect the next time you run `apio sim`.

Apio defines the Verilog macro when running `apio sim` and does not define it when running `apio test`. This allows conditional calls to `$fatal` such that the simulation exits with an error when run in batch mode using `apio test`, but continues and emits the wave file when run using `apio sim`.

Make sure that your testbenches do not call `$dumpfile()` and instead let Apio set the desired location for the generated signal files. Failing to do so may result in Apio being unable to find the file when opening the GTKWave signal viewer or when cleaning the project.

## Example simulation results of a testbench

These results were generated using a testbench and the command `apio sim`.

![](assets/sim-gtkwave.png)

## Instructions for AI

One way to write testbenches is to provide the tested module and instructions to an AI engine and ask it to generate the testbench code. The rules below can be copy-pasted into the AI prompt to inform it of Apio's requirements.

Apio testbench rules:

- **Rule 1**: Define at the top of the file an assertion macro called `EXPECT_EQ`
  that compares and actual and expected values. If the values do not match, print
  an error messages with the expected and actual values as well as the file name
  and line number, and exit using `$fatal`.

- **Rule 2**: Use a boolean signal called `assertion_err` initialized to 0 and
  set it to 1 when an assertion fails.

- **Rule 3**: Any time you use `$fatal`, qualify it with `` if (!`APIO_SIM) $fatal ``.

- **Rule 4**: At the end of the testbench, print the message "End of simulation".

- **Rule 5**: Use `$dumpvars()` with the testbench module name as an argument.

- **Rule 6**: Do not use `$dumpfile()`.

## Example

We gave this module text to ChatGPT and asked it to generate a testbench based on the rules.

```
module Main #(
    parameter integer N = 3_000_000
) (
    input  CLK,        // 12MHz clock
    output [7:0] ROWS, // LED rows
    output [3:0] COLS  // LED columns
);

  reg [31:0] counter = 0;

  reg toggle = 0;

  // Rows and columns are active low.
  assign ROWS = {6'b111111, toggle, ~toggle};
  assign COLS = 4'b1110;

  always @(posedge CLK) begin
    if (counter >= N - 1) begin
      counter <= 0;
      toggle <= !toggle;
    end else begin
      counter <= counter + 1;
    end
  end

endmodule
```

The provided testbench:

```
`timescale 1ns / 1ps

// Rule 1: EXPECT_EQ macro
`define EXPECT_EQ(actual, expected) \
  if ((actual) !== (expected)) begin \
    $display("ERROR at %s:%0d: expected %s = %0b but got %0b", \
             `__FILE__, `__LINE__, `"actual`", expected, actual); \
    assertion_err = 1; \
    if (!`APIO_SIM) $fatal; \
  end

module Main_tb;

  reg CLK = 0;
  wire [7:0] ROWS;
  wire [3:0] COLS;

  // Rule 2: assertion error flag
  reg assertion_err = 0;

  // Clock generation: 12MHz -> 83.33ns period -> 41.67ns half-period
  always #42 CLK = ~CLK;

  // Instantiate the DUT
  Main #(.N(4)) dut (
    .CLK(CLK),
    .ROWS(ROWS),
    .COLS(COLS)
  );

  initial begin
    $dumpvars(0, Main_tb); // Rule 5

    // Wait for stable CLK
    repeat (2) @(posedge CLK);

    // Check initial COLS value
    `EXPECT_EQ(COLS, 4'b1110);

    // Test alternating ROWS behavior
    repeat (4) begin
      reg [7:0] expected_rows;

      expected_rows = {6'b111111, 1'b0, 1'b1}; // toggle = 0
      repeat (4) @(posedge CLK); // wait for N cycles
      `EXPECT_EQ(ROWS, expected_rows);

      expected_rows = {6'b111111, 1'b1, 1'b0}; // toggle = 1
      repeat (4) @(posedge CLK);
      `EXPECT_EQ(ROWS, expected_rows);
    end

    #100;

    $display("End of simulation"); // Rule 4
    $finish;
  end

endmodule
```
