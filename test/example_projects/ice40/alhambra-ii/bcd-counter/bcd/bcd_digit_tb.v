// A testbench for testing the bcd_digit module.

`include "testing/apio_testing.vh"

`timescale 10 ns / 1 ns

module bcd_digit_tb ();

  // This defines a managed signal called 'clk'.
  `DEF_CLK

  // Inputs.
  reg reset = 1;
  reg tick_in = 0;

  // Outputs.
  wire tick_out;
  wire [3:0] count;

  bcd_digit digit (
      .sys_clk(clk),
      .sys_reset(reset),
      .tick_in(tick_in),
      .tick_out(tick_out),
      .count(count)
  );

  initial begin
    // Start the test.
    `TEST_BEGIN(bcd_digit_tb)

    // Reset for 2 clocks.
    `CLKS(2)
    reset = 0;

    // Count 15 times
    repeat (15) begin
      `CLKS(2)
      tick_in = 1;
      `CLK
      tick_in = 0;
      `CLKS(3)
    end

    // Assert on ethe xpected digit value.
    `EXPECT(count, 15 % 10)

    // End of test.
    `TEST_END
  end

endmodule
