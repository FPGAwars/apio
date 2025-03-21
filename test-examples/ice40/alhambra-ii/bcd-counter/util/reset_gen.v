// A module that generates a syncrhonous reset on start.

module reset_gen (
    input sys_clk,
    output reg sys_reset
);

  // Relying on ICE40 behavior of reseting all DFF on power on reset.
  reg [2:0] counter = 0;

  always @(posedge sys_clk) begin
    if (counter < 3) begin
      // Reset active.
      sys_reset <= 1;
      counter   <= counter + 1;
    end else begin
      // Reset inactive.
      sys_reset <= 0;
    end
  end

endmodule
