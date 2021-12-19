/*
    Verilog description of cell library to allow for proper port mapping

    Based on Yosys cmos example
*/

module ltl_BUF(A, Y);
input A;
output Y;
assign Y = A;
endmodule

module ltl_NOT(A, Y);
input A;
output Y;
assign Y = ~A;
endmodule

module ltl_NAND2(A, B, Y);
input A, B;
output Y;
assign Y = ~(A & B);
endmodule

module ltl_NAND3(A, B, C,Y);
input A, B, C;
output Y;
assign Y = ~(A & B & C);
endmodule

module ltl_AOI2_2(A, B, C, D, Y);
input A, B, C, D;
output Y;
assign Y = ~((A & B) | (C & D));
endmodule

module ltl_AOI1_2(A, B, C, Y);
input A, B, C;
output Y;
assign Y = ~((A & B) | (B & C));
endmodule


module ltl_NOR2(A, B, Y);
input A, B;
output Y;
assign Y = ~(A | B);
endmodule

module ltl_NOR3(A, B, C, Y);
input A, B , C;
output Y;
assign Y = ~(A | B | C);
endmodule
/*
module ltl_DFF(C, D, Q);
input C, D;
output reg Q;
always @(posedge C)
	Q <= D;
endmodule
*/
module hy_XOR2(A, B, Y);
input A, B;
output Y;
assign Y = (A ^ B);
endmodule


module ltl_DFFNP(C, D, Q, QN);
input C, D;
output reg Q;
output QN;
always @(posedge C)
    Q <=  D;

assign QN = ~Q;

endmodule