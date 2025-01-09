module blinky #(
    // Num of click cycle per led toggle.
    parameter integer DIV = 13_499_999
) (
    input      sys_clk,
    output reg led         // Active low
);

  // ---- Reset generator.

  reg [3:0] reset_counter = 0;
  reg sys_reset = 1;

  always @(posedge sys_clk) begin
    if (reset_counter < 3) begin
      sys_reset <= 1;
      reset_counter   <= reset_counter + 1;
    end else begin
      sys_reset <= 0;
    end
  end

  // ---- Blinker

  reg [31:0] blink_counter;

  always @(posedge sys_clk) begin
    if (sys_reset) begin
      blink_counter <= 0;
      led <= 1;
    end else if (blink_counter < DIV) begin
      blink_counter <= blink_counter + 1;
    end else begin
      blink_counter <= 0;
      led <= ~led;
    end
  end

endmodule
