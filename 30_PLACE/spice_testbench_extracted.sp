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
.param CB=68p

* input signals

* Vrst rst 0 DC 0
Vrst nrst 0 dc 0 PULSE(5 0 500n 5n 5n 6u 180u)
Vclk clk 0 dc 0 PULSE(0 5 4u 5n 5n 4u 8u)

* Note: No pull up needed on outputs since they are internally connected. B
* Pull ups may have to be added for other designs

Xuut clk nrst out0 out1 out2 main
* Xuut clk nrst out0 out1 out2 out3 main

.tran 500p 100u
* .measure tran maxv MAX out0
* .measure tran out0tr TRIG out0 VAL=0.2*maxv RISE=1 TARG out0 VAL=0.8*maxv RISE=1

.control
run
plot v(clk)+5 v(nrst) v(out0)+10 v(out1)+15 v(out2)+20
* plot v(clk)+5 v(nrst) v(out0)+10 v(out1)+15 v(out2)+20 v(out3)+25
.endc

.end


.end
