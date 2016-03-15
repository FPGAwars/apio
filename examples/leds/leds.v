//-- Hello world program
//-- Turn on all the leds
module leds(output wire LED0,
            output wire LED1,
            output wire LED2,
            output wire LED3,
            output wire LED4);

//-- icestick Red leds
assign LED0 = 1'b1;
assign LED1 = 1'b1;
assign LED2 = 1'b1;
assign LED3 = 1'b1;

//-- Green led
assign LED4 = 1'b1;

endmodule
