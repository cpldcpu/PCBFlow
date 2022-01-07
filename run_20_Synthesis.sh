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
    echo "  RTPG    Bipolar Resistor Transistor Logic with pass gates"
    echo "  nmos    nmos transistor logic"
    echo "  hybrid  hybrid nmos/bipolar logic"
    echo "  amux    analog multiplexer logic"
    echo "  74LVC   74LVC single gate logic"
    echo "  YG      YG strip logic"
    echo "  LTL     LED Transistor Logic"
    echo "  NE      NE555 logic"
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
    echo "Synthesizing to bipolar resistor transistor logic"
elif [ "$APP" == "RTPG" ]; then
    echo "Synthesizing to bipolar resistor transistor/pass gate logic"
elif [ "$APP" == "nmos" ]; then
    echo "Synthesizing to nmos transistor logic"
elif [ "$APP" == "amux" ]; then
    echo "Synthesizing to analog multiplexer logic"
elif [ "$APP" == "74LVC" ]; then
    echo "Synthesizing to single gate TTL logic (74LVC)"
elif [ "$APP" == "hybrid" ]; then
    echo "Synthesizing to hybrid Bipolar/nmos logic"
elif [ "$APP" == "YG" ]; then
    echo "Synthesizing to YG strip logic"
elif [ "$APP" == "LTL" ]; then
    echo "Synthesizing to LED²-Transistor-Logic"
elif [ "$APP" == "NE" ]; then
    echo "Synthesizing to NE555 logic"
else
    echo "Unknown logic style :$APP"
    exit 1
fi


cd Work
ghdl -a --std=02 ../10_HDL/$FILE.vhd         

if [ "$(yosys -H | grep ghdl)" == "" ]; then
    echo "Invoking Yosys with external GHDL plugin"
    yosys -m ghdl ../20_SYNTH/flow_discrete_$APP.ys >208_log_yosys.txt
else
    echo "Yosys has GHDL integrated"
    yosys ../20_SYNTH/flow_discrete_$APP.ys >208_log_yosys.txt   
fi

grep -i 'Printing' -A 28 208_log_yosys.txt
cd ..


