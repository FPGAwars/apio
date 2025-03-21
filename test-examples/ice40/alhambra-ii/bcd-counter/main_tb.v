// A testbench of main.v.

// Import apio friendly testing macros.
`include "apio_testing.vh"

`timescale 10 ns / 1 ns

module main_tb ();

  // This defines a managed signal called 'clk'.
  `DEF_CLK

  // Module's output.
  wire [7:0] leds;

  main #(
      .DIV(3)
  ) main (
      .CLK (clk),
      .LEDS(leds)
  );

  initial begin
    `TEST_BEGIN(main_tb)

    // Free run for 400 clocks.
    `CLKS(400)

    // Assert on expected bcd value.
    `EXPECT(leds, 'h31)

    `TEST_END
  end

endmodule
