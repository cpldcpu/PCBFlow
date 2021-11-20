/*
    Verilog description of cell library to allow for proper port mapping

    Based on Yosys cmos example
*/

module BUF(A, Y);
input A;
output Y;
assign Y = A;
endmodule

module NOT(A, Y);
input A;
output Y;
assign Y = ~A;
endmodule


module XOR2(A, B, Y);
input A, B;
output Y;
assign Y =  (A ^ B);
endmodule


module NOR2(A, B, Y);
input A, B;
output Y;
assign Y = ~(A | B);
endmodule

module NOR3(A, B, C, Y);
input A, B , C;
output Y;
assign Y = ~(A | B | C);
endmodule

module DFF7T(C, D, Q);
input C, D;
output reg Q;
always @(posedge C)
	Q <= D;
endmodule

module DFF(C, D, Q);
input C, D;
output reg Q;
always @(posedge C)
	Q <= D;
endmodule