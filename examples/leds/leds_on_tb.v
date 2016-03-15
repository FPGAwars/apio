//-------------------------------------------------------------------
//-- leds_on_tb.v
//-- Testbench
//-------------------------------------------------------------------
//-- BQ March 2016. Written by Juan Gonzalez (Obijuan)
//-------------------------------------------------------------------
`default_nettype none
`timescale 100 ns / 10 ns

module leds_on_tb();

//-- Simulation time: 1us (10 * 100ns)
parameter DURATION = 10;

//-- Clock signal. It is not used in this simulation
reg clk = 0;
always #0.5 clk = ~clk;

//-- Leds port
wire l0, l1, l2, l3, l4;

//-- Instantiate the unit to test
leds UUT (
           .LED0(l0),
           .LED1(l1),
           .LED2(l2),
           .LED3(l3),
           .LED4(l4)
         );


initial begin

  //-- File were to store the simulation results
  $dumpfile("leds_on_tb.vcd");
  $dumpvars(0, leds_on_tb);

   #(DURATION) $display("End of simulation");
  $finish;
end

endmodule
