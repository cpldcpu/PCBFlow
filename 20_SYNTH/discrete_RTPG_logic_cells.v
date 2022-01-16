/*
    Verilog description of cell library to allow for proper port mapping

    Based on Yosys cmos example
*/

module BUF(A, Y);
input A;
output Y;
assign Y = A;
endmodule

module rtpg_NOT(A, Y);
input A;
output Y;
assign Y = ~A;
endmodule

module rtpg_XOR2(A, B, Y);
input A, B;
output Y;
assign Y =  (A ^ B);
endmodule

module rtpg_NOR2(A, B, Y);
input A, B;
output Y;
assign Y = ~(A | B);
endmodule

module rtpg_NOR3(A, B, C, Y);
input A, B , C;
output Y;
assign Y = ~(A | B | C);
endmodule

module rtpg_NOR4(A, B, C, D, Y);
input A, B , C, D;
output Y;
assign Y = ~(A | B | C | D);
endmodule

module rtpg_DFF7T(nC, D, Q);
input nC, D;
output reg Q;
always @(negedge nC)
	Q <= D;
endmodule

module rtpg_DFF7T_PN(nC, D, Q, QN);
input nC, D;
output reg Q;
output QN;

always @(negedge cC)
	Q <= D;
assign QN = ~Q;

endmodule

module rtpg_DFF7T_CLR(C, CD, D, Q, QN);
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
