/*
    Verilog description of cell library to allow for proper port mapping

    Based on Yosys cmos example
*/

module nm_BUF(A, Y);
input A;
output Y;
assign Y = A;
endmodule

module nm_NOT(A, Y);
input A;
output Y;
assign Y = ~A;
endmodule

module nm_NAND2(A, B, Y);
input A, B;
output Y;
assign Y = ~(A & B);
endmodule

module nm_NAND3(A, B, C,Y);
input A, B, C;
output Y;
assign Y = ~(A & B & C);
endmodule

module nm_AOI2_2(A, B, C, D, Y);
input A, B, C, D;
output Y;
assign Y = ~((A & B) | (C & D));
endmodule

module nm_NOR2(A, B, Y);
input A, B;
output Y;
assign Y = ~(A | B);
endmodule

module nm_NOR3(A, B, C, Y);
input A, B , C;
output Y;
assign Y = ~(A | B | C);
endmodule

module nm_DFF(C, D, Q);
input C, D;
output reg Q;
always @(posedge C)
	Q <= D;
endmodule