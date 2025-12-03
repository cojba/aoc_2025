//------------------------------------------------------------------------------
// Description:
//   This module implements a safe dial puzzle solver. The dial has positions 0-99 and can
//   be rotated left (toward lower numbers) or right (toward higher numbers).
//   The module counts how many times the dial lands on position 0 after
//   rotations.
//
// Parameters:
//   DIAL_SIZE - Number of positions on the dial (default: 100)
//   DIAL_START - Starting position on the dial (default: 50)
//
// Ports:
//   clk_i        - Clock input
//   rst_i        - Synchronous reset (active high)
//   direction_i  - Rotation direction (0=Left, 1=Right)
//   distance_i   - Distance to rotate (can be > DIAL_SIZE)
//   zero_count_o - Number of times dial landed on 0
//------------------------------------------------------------------------------

module safe_dial #(
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
// Internal parameters
//----------------------------------------------------------------------------
localparam int DIAL_SIZE_WIDTH = $clog2(DIAL_SIZE);
localparam int MOD_INPUT_WIDTH = 14;

//----------------------------------------------------------------------------
// Internal signals
//----------------------------------------------------------------------------
logic [6:0] effective_distance;
logic [6:0] position_next_d;
logic [6:0] position_q;
logic [8:0] temp_sum;

// Calculate effective distance using Barrett reduction (handles distances > DIAL_SIZE)
mod_barrett #(
  .M (DIAL_SIZE)
) inst_mod_barrett (
  .x (distance_i[MOD_INPUT_WIDTH-1:0]),
  .r (effective_distance)
);

//----------------------------------------------------------------------------
// Combinatorial process
//----------------------------------------------------------------------------
always_comb begin
  if (direction_i == 1'b0) begin
    // Left rotation: (position - distance) % DIAL_SIZE
    // Add DIAL_SIZE to handle negative results
    temp_sum = {2'b0, position_q} + {2'b0, DIAL_SIZE_WIDTH'(DIAL_SIZE)} - {2'b0, effective_distance};
    position_next_d = (temp_sum >= {2'b0, DIAL_SIZE_WIDTH'(DIAL_SIZE)}) ?
                      temp_sum[6:0] - DIAL_SIZE_WIDTH'(DIAL_SIZE) :
                      temp_sum[6:0];
  end else begin
    // Right rotation: (position + distance) % DIAL_SIZE
    temp_sum = {2'b0, position_q} + {2'b0, effective_distance};
    position_next_d = (temp_sum >= {2'b0, DIAL_SIZE_WIDTH'(DIAL_SIZE)}) ?
                      temp_sum[6:0] - DIAL_SIZE_WIDTH'(DIAL_SIZE) :
                      temp_sum[6:0];
  end
end

//----------------------------------------------------------------------------
// Sequential process
//----------------------------------------------------------------------------
always_ff @(posedge clk_i) begin
  position_q <= position_next_d;
  
  if (position_next_d == '0) begin
    zero_count_o <= zero_count_o + 32'd1;
  end

  if (rst_i) begin
    position_q <= DIAL_SIZE_WIDTH'(DIAL_START);
    zero_count_o <= '0;
  end
end

endmodule
