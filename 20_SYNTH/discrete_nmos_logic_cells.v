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

module nm_AOI1_2(A, B, C, Y);
input A, B, C;
output Y;
assign Y = ~((A & B) | (B & C));
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


module nm_DFFNP(C, D, Q, QN);
input C, D;
output reg Q;
output QN;
always @(posedge C)
    Q <=  D;

assign QN = ~Q;

endmodule

module nm_DFFNP_CLR(C, CD, D, Q, QN);
input C, D, CD;
output reg Q;
output QN;
always @(posedge C or negedge CD)
begin
    if (CD == 1'b0)
        Q <= 1'b0; 
    else
        Q <=  D;
end

assign QN = ~Q;

endmodule

