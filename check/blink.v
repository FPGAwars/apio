
module main (
	input CLK,
	output LED
);

//-- Modify this value for changing the blink frequency
localparam N = 22;  //-- N<=21 Fast, N>=23 Slow

reg [N:0] counter;
always @(posedge CLK)
  counter <= counter + 1;

assign LED = counter[N];

endmodule
