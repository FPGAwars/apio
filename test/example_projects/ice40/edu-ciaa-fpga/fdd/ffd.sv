module ffd(
    input logic clk,
    input logic d,
    output logic q
);

    always_ff @(posedge clk)
        q <= d;

endmodule