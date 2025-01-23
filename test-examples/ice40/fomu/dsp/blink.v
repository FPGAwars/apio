// This example demonstrates the effect the -dsp has on the 
// synthesis phase. See apio.ini for the option definition
// and use 'apio report' to see how yosys shifts the implemeation
// from ICESTORM_DSP and ICESTORM_LC cells. 

module top (

    input  clki,
    input  user_1,  // serial data in.
    output reg    user_2,  // serial data out

    // USB Pins (which should be statically driven if not being used).
    output usb_dp,
    output usb_dn,
    output usb_dp_pu
);

  // Prevent the host from trying to connect to this design.
  assign usb_dp = 1'b0;
  assign usb_dn = 1'b0;
  assign usb_dp_pu = 1'b0;

  // The size of each of the serial registers.
  // TODO: Why this fails with N = 40.
  localparam N = 32;

  // The two words we multiply.
  reg [N-1:0] reg1;
  reg [N-1:0] reg2;

  always @(posedge clki) begin
    // Shift din into 2 x N words 
    reg1   <= {reg1[N-2:0], user_1};
    reg2   <= {reg1[N-2:0], reg1[N-1]};
    // Multiply the words, and output the parity of the result.
    user_2 <= ~^(reg1 * reg2);
  end

endmodule
