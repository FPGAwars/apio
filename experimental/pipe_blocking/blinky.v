//------------------------------------------------------------------
//-- Blinking LED
//------------------------------------------------------------------

module Test (
    input  CLK,   // 12MHz clock
    output LED7,  // LED to blink
    // The rest of the LEDs are turned off.
    output LED6,
    output LED5,
    output LED4,
    output LED3,
    output LED2,
    output LED1,
    output LED0
);

  reg [23:0] counter = 0;

  always @(posedge CLK) counter <= counter + 1;

  assign LED7 = counter[23];

  //-- Turn off the other LEDs
  assign {LED6, LED5, LED4} = 3'b0;
  assign {LED3, LED2, LED1, LED0} = 4'b0;

endmodule


