
module \$_SDFF_NP0_ (input D, input C, input R, output Q, output Qn);
DFFXXX _TECHMAP_REPLACE_ (
    .D(D),
    .C(C),
    .R(R),
    .Q(Q),
    .Qn(Qn),
);
endmodule

module \$_DLATCH_P_ (input E, input D, output Q);
LATCH_N _TECHMAP_REPLACE_ (
.EN(!E),
.D(D),
.Q(Q)
);
endmodule


module \$_DLATCH_N_ (input E, input D, output Q);
LATCH_N _TECHMAP_REPLACE_ (
.EN(E),
.D(D),
.Q(Q)
);
endmodule

module \$_TBUF_ (input A, input E, output Y);
rt_TBUF_N _TECHMAP_REPLACE_ (
.A(A),
.nE(!E),
.Y(Y)
);
endmodule

// module \$add (A, B, Y);   // Uncomment to use ripple adder
module \$___add (A, B, Y);

    parameter A_SIGNED = 0;
    parameter B_SIGNED = 0;
    parameter A_WIDTH = 0;
    parameter B_WIDTH = 0;
    parameter Y_WIDTH = 0;

    input [A_WIDTH-1:0] A;
    input [B_WIDTH-1:0] B;
    output [Y_WIDTH-1:0] Y;
    wire [Y_WIDTH-1:0] 	CO;
    wire [Y_WIDTH-1:0] 	C = {CO, 1'b0};
    wire [Y_WIDTH-1:0] 	HA;

    genvar i;
    generate for (i=0; i<Y_WIDTH; i = i + 1) begin:slice
       assign HA[i] = A[i] ^ B[i];
       assign Y[i] = HA[i] ^ C[i];
    //    assign CO[i] = (A[i] & B[i]) | (A[i] & C[i]) | (B[i] & C[i]);
       assign CO[i] = (A[i] & B[i]) | (HA[i] & C[i]);
    end endgenerate

endmodule

