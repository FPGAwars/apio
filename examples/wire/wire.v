//------------------------------------------------------------------
//-- A simple wire that connects the input with the output
//-- In the icezum board this wire is for connecting the DIO 13 with
//-- the led0
//--
//-- This example has been tested on the following boards:
//--   * Icezum alhambra (https://github.com/FPGAwars/icezum)
//------------------------------------------------------------------

module simplewire(input  wire in,
                  output wire out);

//-- Wire: Connect the input with the output
assign out = in;

endmodule
