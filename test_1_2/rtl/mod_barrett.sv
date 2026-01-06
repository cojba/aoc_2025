//------------------------------------------------------------------------------
// Description: Barrett reduction: r = x mod M (optimized for M=100)
// Let:
//   - m be the fixed modulus (constant).
//   - k = ceil(log2(m)).
//   - μ = floor(2^(2k) / m) (precomputed constant).
//
// For any x with 0 ≤ x < 2^(2k):
//   1. q1 = floor(x / 2^(k-1)) (right shift by k-1)
//   2. q2 = q1 * μ
//   3. q3 = floor(q2 / 2^(k+1)) (right shift by k+1)
//   4. r = x - q3 * m
//   5. If r ≥ m, subtract m; possibly subtract m twice (the classic Barrett bound guarantees ≤ 2 corrections).
//
// Parameters:
//   M - Modulus value
//
// Ports:
//   x - Input, value to be reduced
//   r - Ouput, reduced value
//------------------------------------------------------------------------------

module mod_barrett #(
  parameter int M = 100
) (
  input  logic [13:0] x,  // XW = 2*K = 14 bits for M=100 (K=7)
  output logic [6:0]  r   // K = 7 bits for M=100
);

// K = ceil(log2(M)) = 7 for M=100
// μ = floor(2^(2K) / M) = floor(2^14 / 100) = floor(16384 / 100) = 163
localparam int K_VAL = 7;
localparam int MU_VAL = 163;
localparam int SHIFT_K_MINUS_1 = 6;
localparam int SHIFT_K_PLUS_1 = 8;

// q1 = floor(x / 2^(K-1)) = x >> 6
logic [7:0] q1;
assign q1 = x[13:SHIFT_K_MINUS_1];

// q2 = q1 * MU (only upper bits needed for next shift)
/* verilator lint_off UNUSEDSIGNAL */
logic [15:0] q2;
/* verilator lint_on UNUSEDSIGNAL */
assign q2 = 16'(q1 * MU_VAL);

// q3 = floor(q2 / 2^(K+1)) = q2 >> 8
logic [7:0] q3;
assign q3 = q2[15:SHIFT_K_PLUS_1];

// q3 * M
logic [14:0] q3m;
assign q3m = 15'(q3 * M);

// x extended to 15 bits
logic [14:0] x_ext;
assign x_ext = {1'b0, x};

// r0 = x - q3*m
logic [14:0] r0;
assign r0 = x_ext - q3m;

// Final correction: subtract M once or twice
// Use full width r0 for comparisons, not truncated version
/* verilator lint_off UNUSEDSIGNAL */
logic [14:0] r1, r2;
/* verilator lint_on UNUSEDSIGNAL */

assign r1 = (r0 >= 15'(M)) ? (r0 - 15'(M)) : r0;
assign r2 = (r1 >= 15'(M)) ? (r1 - 15'(M)) : r1;

// Output is guaranteed to be < M, so safe to truncate to K bits
assign r = r2[K_VAL-1:0];

endmodule
