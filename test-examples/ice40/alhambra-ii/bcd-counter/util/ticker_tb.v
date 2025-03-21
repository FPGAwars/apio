// A testbench for testing the ticker module.

`include "testing/apio_testing.vh"

`timescale 10 ns / 1 ns

module ticker_tb ();

  // This defines a managed signal called 'clk'.
  `DEF_CLK

  // Inputs.
  reg  reset = 1;

  // Outputs.
  wire tick;

  // Instantiate a ticker that generates a tick every 5 clocks.
  ticker #(
      .DIV(5)
  ) ticker (
      .sys_clk(clk),
      .sys_reset(reset),
      .tick(tick)
  );

  initial begin
    `TEST_BEGIN(ticker_tb)

    // Reset for 2 clocks.
    `CLKS(2)
    reset = 0;

    // Free run for 30 clocks.
    `CLKS(30)

    `TEST_END
  end

endmodule
