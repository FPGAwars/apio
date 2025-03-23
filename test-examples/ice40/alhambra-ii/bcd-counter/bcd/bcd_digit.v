// A single cascadable decimal digit counter, 0-9.

module bcd_digit (
    input  wire       sys_clk,    // Continious system clock.
    input  wire       sys_reset,  // Syncrhonous global reset.
    input  wire       tick_in,    // When high, counting one step.
    output wire       tick_out,   // When high, higher order digit should count.
    output reg  [3:0] count       // Count output, 0-9.
);

  // Cascading tick condition.
  assign tick_out = (count == 9) && tick_in;

  // Sequential logic.
  always @(posedge sys_clk) begin
    if (sys_reset) begin
      // Case 1: Reset.
      count <= 0;
    end else if (tick_in) begin
      // Case 2: Count modulue 10
      count <= count >= 9 ? 0 : count + 1;
    end
  end

endmodule


