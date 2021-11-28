
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
TBUF _TECHMAP_REPLACE_ (
.A(A),
.E(E),
.Y(Y)
);
endmodule
