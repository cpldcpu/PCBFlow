* Spice testbench for discrete logic counterx
* Bases on Yosys "CMOS" example

* supply voltages
.global Vee Vcc
Vee Vee 0 DC 0
Vcc Vcc 0 DC 5

* load design and library
.include ../20_SYNTH/discrete_logic_spice_subckt.lib
.include ../20_SYNTH/RTL_NPN.lib
.include 209_synthesized_output.sp

* Define base and load resistor
.param RL=4.7k
.param RB=4.7k

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
.endc

.end
