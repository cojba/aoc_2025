//------------------------------------------------------------------------------
// Module: safe_dial
//------------------------------------------------------------------------------
// Description:
//   Implements a safe dial puzzle solver. The dial has positions 0-99 and can
//   be rotated left (toward lower numbers) or right (toward higher numbers).
//   The module counts how many times the dial lands on position 0 after
//   rotations.
//
// Parameters:
//   DIAL_SIZE - Number of positions on the dial (default: 100)
//
// Ports:
//   clk_i       - Clock input
//   rst_i       - Synchronous reset (active high)
//   valid_i     - Indicates rotation command is valid
//   direction_i - Rotation direction (0=Left, 1=Right)
//   distance_i  - Distance to rotate (0-99)
//   ready_o     - Module is ready for new command
//   position_o  - Current dial position
//   zero_count_o - Number of times dial landed on 0
//------------------------------------------------------------------------------

module safe_dial #(
  parameter int DIAL_SIZE = 100,
  parameter int DISTANCE_WIDTH = 7  // ceil(log2(100)) = 7 bits
) (
  input  logic                      clk_i,
  input  logic                      rst_i,
  input  logic                      valid_i,
  input  logic                      direction_i,  // 0=L (left), 1=R (right)
  input  logic [DISTANCE_WIDTH-1:0] distance_i,
  output logic                      ready_o,
  output logic [DISTANCE_WIDTH-1:0] position_o,
  output logic [31:0]               zero_count_o
);

  //----------------------------------------------------------------------------
  // Internal Signals
  //----------------------------------------------------------------------------
  logic [DISTANCE_WIDTH-1:0] position_q;
  logic [31:0]               zero_count_q;

  //----------------------------------------------------------------------------
  // Dial Position and Zero Counter Logic
  //----------------------------------------------------------------------------
  always_ff @(posedge clk_i) begin
    if (rst_i) begin
      position_q <= 7'd50;      // Start at position 50
      zero_count_q <= 32'd0;
    end else if (valid_i) begin
      logic [DISTANCE_WIDTH-1:0] next_pos;
      
      // Calculate next position based on direction
      if (direction_i == 1'b0) begin
        // Left rotation (toward lower numbers)
        if (position_q >= distance_i) begin
          next_pos = position_q - distance_i;
        end else begin
          // Wrap around: (position - distance + DIAL_SIZE) % DIAL_SIZE
          next_pos = DIAL_SIZE[DISTANCE_WIDTH-1:0] - (distance_i - position_q);
        end
      end else begin
        // Right rotation (toward higher numbers)
        if (position_q + distance_i < DIAL_SIZE) begin
          next_pos = position_q + distance_i;
        end else begin
          // Wrap around: (position + distance) % DIAL_SIZE
          next_pos = (position_q + distance_i) - DIAL_SIZE[DISTANCE_WIDTH-1:0];
        end
      end
      
      // Update position
      position_q <= next_pos;
      
      // Increment zero counter if landing on position 0
      if (next_pos == 7'd0) begin
        zero_count_q <= zero_count_q + 1;
      end
    end
  end

  //----------------------------------------------------------------------------
  // Output Assignments
  //----------------------------------------------------------------------------
  assign ready_o = 1'b1;  // Always ready in this simple implementation
  assign position_o = position_q;
  assign zero_count_o = zero_count_q;

endmodule
