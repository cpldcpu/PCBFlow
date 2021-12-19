* Spice testbench for discrete logic counterx
* Bases on Yosys "CMOS" example

* supply voltages
.global Vee Vcc gnd
Vee Vee 0 DC 0
Vcc Vcc 0 DC 5

* load design and library
.include ../20_SYNTH/microcell_spice_subckt.lib
.include ../20_SYNTH/2N7002.lib
* .include ../20_SYNTH/PMBT2369.lib
.include ../20_SYNTH/PMBT3904.lib
.include ../20_SYNTH/LTL_LED.lib
.include ../20_SYNTH/amux.lib
.include 308_extracted_netlist.sp

* Define base and load resistor
.param RL=3.3k
.param RB=3.3k

* input signals

Vclk clk 0 PULSE(0 5 10u 20n 20n 8u 20u)
Vrst rst 0 PULSE(0 5 5u 20n 20n 29u 400u)

* Note: No pull up needed on outputs since they are internally connected. B
* Pull ups may have to be added for other designs

Xuut clk rst out0 out1 out2 main

.tran 20n 400u

.control
run
plot v(clk)+5 v(rst) v(out0)+10 v(out1)+15 v(out2)+20 
plot i(vcc)
.endc

.end
