//------------------------------------------------------------------
//-- Blinking LED
//------------------------------------------------------------------

module Test (
  input CLK,    // 100MHz clock
  output led   // LED to blink
);

  reg [25:0] counter = 0;

  always @(posedge CLK) 
    counter <= counter + 1;

  assign led = counter[25];

endmodule
