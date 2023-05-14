* Spice testbench for mcpu

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
* .param RL=3.3k
* .param RB=3.3k
*.param CB=68p

.param RL=4.7k
.param RB=4.7k
.param CB=68p

* input signals

* Vrst rst 0 DC 0
Vrst rst 0 dc 0 PULSE(5 0 500n 5n 5n 6u 180u)
* Vclk clk 0 dc 0 PULSE(5 2 1u 5n 5n 4u 8u)
Vclk clk 0 dc 0 PULSE(0 5 4u 150n 150n 4u 8u)

*Vdat6 data.6 0 dc 0 
Vdat7 data.7 0 dc 0 
* Note: No pull up needed on outputs since they are internally connected. B
* Pull ups may have to be added for other designs

RPwe Vcc we {RL}
RPoe Vcc oe {RL}

Xuut rst clk data.0 data.1 data.2 data.3 data.4 data.5 data.6 data.7 adress.0 adress.1 adress.2 adress.3 adress.4 adress.5 oe we main
*Xuut clk nrst out0 out1 out2 main
* Xuut clk nrst out0 out1 out2 out3 main

.tran 500p 50u
* .measure tran maxv MAX out0
* .measure tran out0tr TRIG out0 VAL=0.2*maxv RISE=1 TARG out0 VAL=0.8*maxv RISE=1

.control
run
plot v(clk)+5 v(rst) v(adress.0)+10 v(adress.1)+15 v(adress.2)+20 v(adress.3)+25 v(adress.4)+30 v(adress.5)+35
plot v(clk)+5 v(rst) v(data.0)+10 v(data.1)+15 v(data.2)+20 v(data.3)+25 v(data.4)+30 v(data.5)+35 v(data.6)+40 v(data.7)+45  
plot v(clk)+5 v(rst) v(Xuut._33.A.0)+10 v(Xuut._33.A.1)+15 v(Xuut._33.A.2)+20 v(Xuut._33.A.3)+25 v(Xuut._33.A.4)+30 v(Xuut._33.A.5)+35 v(Xuut._33.A.6)+40 v(Xuut._33.A.7)+45  
plot v(clk)+5 v(rst) v(oe)+10 v(we)+15 
plot i(vee)
*plot v(clk)+5 v(nrst) v(out0)+10 v(out1)+15 v(out2)+20
* plot v(clk)+5 v(nrst) v(out0)+10 v(out1)+15 v(out2)+20 v(out3)+25
.endc

.end


.end
