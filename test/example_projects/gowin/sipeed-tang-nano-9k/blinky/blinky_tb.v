// A testbench for testing the blinky module.

`include "apio_testing.vh"

`timescale 10 ns / 1 ns

module blinky_tb ();

  // This defines a managed signal called 'clk'.
  `DEF_CLK

  // Outputs.
  wire led;

  // Instantiate a blinky that toggles the led every 5 clocks.
  blinky #(
      .DIV(5)
  ) ticker (
      .sys_clk(clk),
      .led(led)
  );

  initial begin
    `TEST_BEGIN(blinky_tb)

    // Free run for 50 clocks.
    `CLKS(30)

    `TEST_END
  end

endmodule
