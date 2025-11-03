// An examples that require high propogation delay to compute the 
// parity of a large word. Should result in lower max clock speed than
// usual.

module parity (
    input      sys_clk,
    output reg led  // Active low
);

  // Placement fails around 269.
  reg [260:0] counter = 0;

  always @(posedge sys_clk) begin
    counter <= counter + 1;
    led <= ^counter;
  end

endmodule
