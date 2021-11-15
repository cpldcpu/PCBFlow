#!/bin/bash
# Run Synthesis from VHDL to Discrete Logic
# Invokes GHDL, Yosys and ABC (via Yosys)
#  

# --->>>>  Requires name of HDL source file as argument <<<<---

# set HDLCODE = "counter.vhd"  # Name of source file from "10_HDL"

if [ "$1" == "" ]; then
    echo "Usage: run_20_Synthesis.sh design [technology] "
    echo "  'design' is the name of your VHDL sourcecode without extension."
    echo "  'technology' selects technology (optional)"
    echo ""
    echo "Technologies:"
    echo "  RT      Bipolar Resistor Transistor Logic (default)"
    echo "  nmos    nmos transistor logic"
    echo "  amux    analog multiplexer logic"
    echo "  74LVC   74LVC single gate logic"
    exit 1
else
    FILE="$1"
fi


if [ "$2" == "" ]; then
    APP="RT"
else
    APP="$2"
fi

if [ "$APP" == "RT" ]; then
    echo "Synthesizing to Resistor Transistor Logic"
elif [ "$APP" == "nmos" ]; then
    echo "Synthesizing to nmos transistor logic"
elif [ "$APP" == "amux" ]; then
    echo "Synthesizing to analog multiplexer logic"
elif [ "$APP" == "74LVC" ]; then
    echo "Synthesizing to single gate TTL logic (74LVC)"
else
    echo "Unknown logic style :$APP"
    exit 1
fi




cd Work
ghdl -a ../10_HDL/$FILE.vhd
yosys ../20_SYNTH/flow_discrete_$APP.ys >208_log_yosys.txt
grep -i 'Printing' -A 20 208_log_yosys.txt
cd ..

# ngspice testbench_rtl.sp 
