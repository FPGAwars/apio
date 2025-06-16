// A module that provide the counter tick signal.
// The tick output is high for one clock every one second.

module ticker #(
    // The number of clocks per tick. Controls the tick speed.
    // Verilog require that we will specify here a value even though we
    // override it in main.v.
    parameter integer DIV = 12000000
) (
    input  wire sys_clk,    // 12MHz clock
    input  wire sys_reset,  // Syncrhonous global reset
    output reg  tick        // High for one clock every DIF clocks.
);

  // Clock divider counter.
  reg [31:0] counter = 0;

  // Sequential logic.
  always @(posedge sys_clk) begin
    if (sys_reset) begin
      // Case 1: Reset.
      counter <= 0;
      tick <= 0;
    end else if (counter >= (DIV - 1)) begin
      // Case 2: Cycle end.
      counter <= 0;
      tick <= 1;
    end else begin
      // Case 3: Normal increment.
      counter <= counter + 1;
      tick <= 0;
    end
  end

endmodule


