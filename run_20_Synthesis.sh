#!/bin/sh
# Run Synthesis from VHDL to Discrete Logic
# Invokes GHDL, Yosys and ABC (via Yosys)
#  

# --->>>>  Requires name of HDL source file as argument <<<<---

# set HDLCODE = "counter.vhd"  # Name of source file from "10_HDL"

cd Work
ghdl -a ../10_HDL/$1.vhd
yosys ../20_SYNTH/flow_discrete.ys >208_log_yosys.txt
grep -i 'Printing' -A 20 208_log_yosys.txt
cd ..

# ngspice testbench_rtl.sp 
