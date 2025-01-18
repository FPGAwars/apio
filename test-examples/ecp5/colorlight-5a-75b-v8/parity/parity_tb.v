// A testbench for testing the parity module.

`include "apio_testing.vh"

`timescale 10 ns / 1 ns

module parity_tb ();

  // This defines a managed signal called 'clk'.
  `DEF_CLK

  // Outputs.
  wire led;

  // Instantiate a parity that toggles the led every 5 clocks.
  parity parity (
      .sys_clk(clk),
      .led(led)
  );

  initial begin
    `TEST_BEGIN(parity_tb)

    // Free run for 30 clocks.
    `CLKS(30)

    `TEST_END
  end

endmodule
