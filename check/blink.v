
module main (
	input CLK,
	output LED,
);

//-- Modify this value for changing the blink frequency
localparam N = 22;  //-- N<=21 Fast, N>=23 Slow

reg 
always @(posedge CLK)
  r_LED_state <= !r_LED_state;

assign PMOD1 = r_LED_state;
assign PMOD2 = r_LED_state2;

endmodule
