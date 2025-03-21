// Utility macros for testbenches that are compatible with apio.

`default_nettype none

`define DUMP_FILE_NAME(x) `"x.vcd`"

// Call this macro at the begining of the testbench macro. It defines
// a clk signal and a variable clk_num that indicates the clock num.
`define DEF_CLK \
    reg clk = 0; \
    integer clk_num = 0; \
    always begin \
        #10 clk = ~clk; \
        if (clk) clk_num += 1; \
    end

// Asserts that the value of 'signal' is 'value'. If not, it prints an error message and aborts
// the simulation. When running under apio sim, the macro INTERACTIVE_SIM is defined
// and the failed assertions does not exist to allow showing the sigmulation results
// in the graphical window.
`define EXPECT(signal, value) \
    if (signal !== (value)) begin \
        $display("*** ASSERTION FAILED in %m (clk_num=%0d): expected (signal == value), actual: 'h%h", (clk_num), (signal)); \
        `ifndef INTERACTIVE_SIM \
             $fatal; \
        `endif \
    end

// Transition from clock low to clock high. Typically this is not
// called directly and clock is managed using `CLK().
`define CLK_HIGH \
    begin \
        `EXPECT(clk, 0); \
        @ (posedge clk); \
        #2; \
        `EXPECT(clk, 1); \
    end

// Transition from clock high to clock low. Typically this is not
// called directly and clock is managed using `CLK().
`define CLK_LOW \
    begin \
        `EXPECT(clk, 1); \
        @ (negedge clk); \
        #2; \
        `EXPECT(clk, 0); \
    end

// Simulate one clock. Wait for low to high and then high to low transition.
`define CLK \
    begin \
        `CLK_HIGH \
        `CLK_LOW \
    end

// Simulate n clocks.
`define CLKS(n) \
    begin \
        repeat(n) begin \
            `CLK \
        end \
    end

// Place this macro immediatly after the 'initial begin' statement of the testbench.
// 'testbench' is the name of the testbench module. The macro sets the file
// that will contains the simulation results.
// The macro VCD_OUTPUT is defined automatically by the apio commands sim and test
// and contains base name of the expected output file.
`define TEST_BEGIN(testbench) \
    begin \
            $dumpvars(0, testbench); \
    end

// Place this macro at the end of the 'initial begin' block of the testbench.
`define TEST_END \
    begin \
        @ (posedge clk); \
        $display("End of simulation"); \
        $finish; \
    end
