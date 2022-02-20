
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
.E(!E),
.Y(Y)
);
endmodule
