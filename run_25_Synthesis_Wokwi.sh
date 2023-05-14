#!/bin/bash
# Run Synthesis from VHDL to Discrete Logic
# Invokes GHDL, Yosys and ABC (via Yosys)
#  

# --->>>>  Requires name of HDL source file as argument <<<<---

# set HDLCODE = "counter.vhd"  # Name of source file from "10_HDL"

if [ "$1" == "" ]; then
    echo "Usage: run_20_Synthesis.sh design [technology] "
    echo "  'design' is the ID of your Wokwi project."
    echo "  'technology' selects technology (optional)"
    echo ""
    echo "Technologies:"
    echo "  RT      Bipolar Resistor Transistor Logic (default)"
    echo "  RTPG    Bipolar Resistor Transistor Logic with pass gates"
    echo "  nmos    nmos transistor logic"
    echo "  amux    analog multiplexer logic"
    echo "  74LVC   74LVC single gate logic"
    echo "  YG      YG strip logic"
    echo "  LTL     LED Transistor Logic"
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
elif [ "$APP" == "LTL" ]; then
    echo "Synthesizing to LED²-Transistor-Logic"
else
    echo "Unknown logic style :$APP"
    exit 1
fi


cd Work

echo "Fetching verilog from Wokwi"
curl https://wokwi.com/api/projects/$FILE/verilog >design.v

yosys ../20_SYNTH/flow_v_discrete_$APP.ys >208_log_yosys.txt   

grep -i 'Chip area' -A 4 -B 16 208_log_yosys.txt
cd ..


