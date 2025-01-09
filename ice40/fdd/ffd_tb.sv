`default_nettype none
`timescale 100 ns / 10 ns

module testbench();

parameter DURATION = 10;

logic clk = 0;
always #0.5 clk = ~clk;

logic d, q;

ffd UUT (
    .clk(clk),
    .d(d),
    .q(q)
);

integer i;
reg [1:0] i_b;

initial begin

    $dumpvars(0, testbench);

    for (i=0; i<100; i=i+1)
    begin
        $display ("Current loop # %0d", i);
        $display ("Current loop # %0b", i);
        
        #1
        i_b = i;
        d = i_b[0];
    end

    #(DURATION) $display("End of simulation");
    $finish;
end

endmodule