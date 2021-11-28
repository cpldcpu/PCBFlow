/*
    Verilog description of cell library to allow for proper port mapping

    Based on Yosys cmos example
*/

module am_BUF(A, Y);
input A;
output Y;
assign Y = A;
endmodule

module am_NOT(A, Y);
input A;
output Y;
assign Y = ~A;
endmodule

module am_NAND2(A, B, Y);
input A, B;
output Y;
assign Y = ~(A & B);
endmodule

module am_AND2(A, B, Y);
input A, B;
output Y;
assign Y = (A & B);
endmodule

module am_OR2(A, B, Y);
input A, B;
output Y;
assign Y = (A | B);
endmodule

module am_ORN2(A, B, Y);
input A, B;
output Y;
assign Y = (~A | B);
endmodule


module am_ANDN2(A, B, Y);
input A, B;
output Y;
assign Y = (~A & B);
endmodule


module am_NOR2(A, B, Y);
input A, B;
output Y;
assign Y = ~(A | B);
endmodule

module am_DFF(C, D, Q);
input C, D;
output reg Q;
always @(posedge C)
	Q <= D;
endmodule

module am_MUX2(A, B, S, Y);
input A, B , S;
output Y;
assign Y = (A & S) | (B & ~S);
endmodule

module am_XNOR2(A, B, Y);
input A, B;
output Y;
assign Y = ~(A ^ B);
endmodule
