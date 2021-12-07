/*
    Verilog description of cell library to allow for proper port mapping

    Based on Yosys cmos example
*/

module ne_BUF(A, Y);
input A;
output Y;
assign Y = A;
endmodule

module ne_NOT(A, Y);
input A;
output Y;
assign Y = ~A;
endmodule

module ne_NAND2(A, B, Y);
input A, B;
output Y;
assign Y = ~(A & B);
endmodule

module ne_NAND3(A, B, C,Y);
input A, B, C;
output Y;
assign Y = ~(A & B & C);
endmodule


module ne_NOR2(A, B, Y);
input A, B;
output Y;
assign Y = ~(A | B);
endmodule

module ne_NOR3(A, B, C, Y);
input A, B , C;
output Y;
assign Y = ~(A | B | C);
endmodule

module ne_DFF(C, D, Q);
input C, D;
output reg Q;
always @(posedge C)
	Q <= D;
endmodule
