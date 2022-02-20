/*
    Verilog description of cell library to allow for proper port mapping

    Based on Yosys cmos example
*/

module BUF(A, Y);
input A;
output Y;
assign Y = A;
endmodule

module rt_TBUF_N(A, nE, Y);
input A, nE;
output Y;
assign Y = nE ? 1'bZ : A ;
endmodule

module rt_NOT(A, Y);
input A;
output Y;
assign Y = ~A;
endmodule

module rt_XOR2(A, B, Y);
input A, B;
output Y;
assign Y =  (A ^ B);
endmodule


module rt_NOR2(A, B, Y);
input A, B;
output Y;
assign Y = ~(A | B);
endmodule

module rt_NOR3(A, B, C, Y);
input A, B , C;
output Y;
assign Y = ~(A | B | C);
endmodule

module rt_DFF7T(C, D, Q);
input C, D;
output reg Q;
always @(posedge C)
	Q <= D;
endmodule

module rt_DFF(C, D, Q);
input C, D;
output reg Q;
always @(posedge C)
	Q <= D;
endmodule

module rt_DFF6NOR_NP(C, D, Q, QN);
input C, D;
output reg Q;
output QN;
always @(negedge C)
    Q <=  D;

assign QN = ~Q;

endmodule

module rt_DFFNP6NOR_CLR(C, CD, D, Q, QN);
input C, D, CD;
output reg Q;
output QN;
always @(negedge C or negedge CD)
begin
    if (CD == 1'b0)
        Q <= 1'b0; 
    else
        Q <=  D;
end

assign QN = ~Q;

endmodule
