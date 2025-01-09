`default_nettype none
`timescale 100 ns / 10 ns

module and_gate_testbench();

    logic a, b, s;

    // Instantiate device under test
    and_gate dut(a, b, s);

    // Apply inputs one at a time
    initial begin
        $dumpvars(0, and_gate_testbench);

        a = 0; b = 0;
        #10;
        a = 0; b = 1;
        #10;
        a = 1; b = 0;
        #10;
        a = 1; b = 1;
        #10;

        $display("End of simulation");
        $finish;

    end
endmodule