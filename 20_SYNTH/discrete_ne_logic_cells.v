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

module ne_NAND3(A, B, C, Y);
input A, B, C;
output Y;
assign Y = ~(A & B & C);
endmodule

module ne_NAND4(A, B, C, D, Y);
input A, B, C, D;
output Y;
assign Y = ~(A & B & C & D);
endmodule

module ne_ANDN2(A, B,  Y);
input A, B;
output Y;
assign Y = (A & ~B);
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

module ne_DFF_clear(C, CD, D, Q);
input C, D, CD;
output reg Q;
always @(posedge C or negedge CD)
    begin
        if (CD == 1'b0)
            Q <= 1'b0; 
        else
            Q <=  D;
    end
endmodule



