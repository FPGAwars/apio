// A design that controls the 8 leds with a two digit decimal counter.

module main #(
    // The dividing factor to reach 1 hz from 12Mhz clock. By defining
    // it as a parameter we can reduce it in testbench simulations.
    parameter integer DIV = 12000000
) (
    input        CLK,  // 12MHz clock
    output [7:0] LEDS  // LED to blink
);

  // Global reset from the reset generator.
  wire sys_reset;

  // Cascading count ticks. 
  wire tick1;
  wire tick2;
  wire tick3;

  // Global reset generator.
  reset_gen reset_gen (
      .sys_clk  (CLK),
      .sys_reset(sys_reset)
  );

  // Timing generator. Tick is 
  ticker #(
      .DIV(DIV)
  ) ticker (
      .sys_clk(CLK),
      .sys_reset(sys_reset),
      .tick(tick1)
  );

  // The units digit counter.
  bcd_digit digit1 (
      .sys_clk(CLK),
      .sys_reset(sys_reset),
      .tick_in(tick1),
      .tick_out(tick2),
      .count(LEDS[3:0])
  );

  // The tens digit counter.
  bcd_digit digit2 (
      .sys_clk(CLK),
      .sys_reset(sys_reset),
      .tick_in(tick2),
      .tick_out(tick3),
      .count(LEDS[7:4])
  );




endmodule


