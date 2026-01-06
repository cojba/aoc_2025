//------------------------------------------------------------------------------
// Safe dial v2 - Counts zeros passed through during rotations
//------------------------------------------------------------------------------

module safe_dial_v2 #(
  parameter int DIAL_SIZE = 100,
  parameter int DIAL_START = 50
) (
  input  logic        clk_i,
  input  logic        rst_i,
  input  logic        direction_i,
  /* verilator lint_off UNUSEDSIGNAL */
  input  logic [31:0] distance_i,
  /* verilator lint_on UNUSEDSIGNAL */
  output logic [31:0] zero_count_o
);

//----------------------------------------------------------------------------
// Functions
//----------------------------------------------------------------------------
// q = floor(n/100), n is 32-bit unsigned value
function automatic logic [31:0] div100_u32 (input logic [31:0] n);
  // Magic: 0x51EB851F ; shift = 37 (valid for all 0..2^32-1)
  /* verilator lint_off UNUSEDSIGNAL */
  logic [63:0] prod = n * 32'd1374389535; // 0x51EB_851F
  return {5'b0, prod[63:37]};                     // >> 37
  /* verilator lint_on UNUSEDSIGNAL */
endfunction

//----------------------------------------------------------------------------
// Registers
//----------------------------------------------------------------------------
logic [6:0] position_q;

//----------------------------------------------------------------------------
// Calculate effective distance using Barrett reduction
//----------------------------------------------------------------------------
logic [6:0] effective_distance;

mod_barrett #(
  .M(DIAL_SIZE)
) inst_mod_barrett (
  .x(distance_i[13:0]),
  .r(effective_distance)
);

//----------------------------------------------------------------------------
// Count full wraps (each wrap passes through 0)
//----------------------------------------------------------------------------
logic [31:0] full_wraps;
assign full_wraps = div100_u32(distance_i);

//----------------------------------------------------------------------------
// Check if effective distance crosses 0
//----------------------------------------------------------------------------
logic crosses_zero_from_effective;

always_comb begin
  crosses_zero_from_effective = 1'b0;

  if (effective_distance > 7'd0) begin
    if (direction_i == 1'b1) begin
      // Right: cross if position + effective >= 100
      if (({1'b0, position_q} + {1'b0, effective_distance}) >= 8'd100) begin
        crosses_zero_from_effective = 1'b1;
      end
    end else begin
      // Left: cross if effective >= position (includes landing exactly on 0)
      if (effective_distance >= position_q) begin
        crosses_zero_from_effective = 1'b1;
      end
    end
  end
end

//----------------------------------------------------------------------------
// Total zeros crossed
//----------------------------------------------------------------------------
logic [31:0] rotation_zeros;

always_comb begin
  if (position_q == 7'd0) begin
    // Starting at 0: only count full wraps
    rotation_zeros = full_wraps;
  end else begin
    // Not starting at 0: count wraps + crossing from effective
    rotation_zeros = full_wraps + {31'd0, crosses_zero_from_effective};
  end
end

//----------------------------------------------------------------------------
// Calculate next position
//----------------------------------------------------------------------------
logic [6:0] next_position;
logic [8:0] temp_sum;

always_comb begin
  if (direction_i == 1'b0) begin
    // Left rotation
    temp_sum = {2'b0, position_q} + 9'd100 - {2'b0, effective_distance};
    next_position = (temp_sum >= 9'd100) ? temp_sum[6:0] - 7'd100 : temp_sum[6:0];
  end else begin
    // Right rotation
    temp_sum = {2'b0, position_q} + {2'b0, effective_distance};
    next_position = (temp_sum >= 9'd100) ? temp_sum[6:0] - 7'd100 : temp_sum[6:0];
  end
end

//----------------------------------------------------------------------------
// Sequential logic
//----------------------------------------------------------------------------
always_ff @(posedge clk_i) begin
  if (rst_i) begin
    position_q <= 7'(DIAL_START);
    zero_count_o <= 32'd0;
  end else begin
    position_q <= next_position;
    zero_count_o <= zero_count_o + rotation_zeros;
  end
end

endmodule
