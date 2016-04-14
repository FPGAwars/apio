//-------------------------------------------------------------------
//-- leds_on_tb.v
//-- Testbench
//-------------------------------------------------------------------
//-- Juan Gonzalez (Obijuan). April-2016
//-- GPL license
//-------------------------------------------------------------------
`default_nettype none
`timescale 100 ns / 10 ns

module wire_tb();

//-- Simulation time: 1us (10 * 100ns)
parameter DURATION = 10;

//-- Clock signal. It is not used in this simulation
reg clk = 0;
always #0.5 clk = ~clk;

//-- wures
reg in;
wire out;

//-- Instantiate the unit to test
simplewire UUT (
           .in(in),
           .out(out)
         );


initial begin

  //-- File were to store the simulation results
  $dumpfile("wire_tb.vcd");
  $dumpvars(0, wire_tb);

  //-- Set the cable to 0
  in <= 0;

  //-- Set the cable to 1
  #10 in <= 1;

   #(DURATION) $display("End of simulation");
  $finish;
end

endmodule
