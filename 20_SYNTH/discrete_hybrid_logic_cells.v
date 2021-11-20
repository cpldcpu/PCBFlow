/*
    Verilog description of cell library to allow for proper port mapping

    Based on Yosys cmos example
*/

module hy_XOR2(A, B, Y);
input A, B;
output Y;
assign Y = (A ^ B);
endmodule


module hy_DFF7T(C, D, Q);
input C, D;
output reg Q;
always @(posedge C)
	Q <= D;
endmodule