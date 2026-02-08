// Tests the speed of N bits adder.
// To run:
//   apio report -e width-256
//   apio report -e width-128
//   apio report -e width-32
//   apio report -e width-16
//   apio report -e width-8

module main #(
    parameter WIDTH = `WIDTH
) (
    input  CLK,  // System clock
    output LED   // Output
);

  reg [WIDTH-1:0] counter = 0;

  assign LED = counter[WIDTH-1];

  always @(posedge CLK) begin
    counter <= counter + 7;
  end


endmodule


