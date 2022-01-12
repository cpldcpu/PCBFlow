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

* Vrst rst 0 DC 0
Vrst nrst 0 dc 0 PULSE(5 0 500n 5n 5n 3u 80u)
Vclk clk 0 dc 0 PULSE(0 5 2u 5n 5n 4u 8u)

* Note: No pull up needed on outputs since they are internally connected. B
* Pull ups may have to be added for other designs

Xuut clk nrst out0 out1 out2 main

.tran 500p 26u
* .measure tran maxv MAX out0
* .measure tran out0tr TRIG out0 VAL=0.2*maxv RISE=1 TARG out0 VAL=0.8*maxv RISE=1

.control
let startv = 3V
let endv = 6V
let ixx = startv
let step = 0.5V

echo "VCC, out0 tr [ns], out0 tf [ns], out0 delay rise [ns], out0 delay fall [ns], MaxV [V], AvgI [mA]" >> out.txt
    while ixx le endv
        alter Vcc = ixx
        alter @Vclk[puse] = [0 1 4u 5n 5n 4u 8u]
        alter Vclk = [0 1 4u 5n 5n 4u 8u]
        run
        meas tran maxv MAX out0
        meas tran avgi AVG i(vcc)
        let trigmin = 0.2 * maxv 
        let trigmax = 0.8 * maxv
        meas tran out0tr TRIG out0 td=2550n VAL=trigmin RISE=LAST TARG out0 VAL=trigmax RISE=LAST
        meas tran out0tf TRIG out0 TD=2550n VAL=trigmax FALL=LAST TARG out0 VAL=trigmin FALL=LAST
        meas tran out0tdrise TRIG clk td=2550n VAL=trigmin RISE=1 TARG out0 VAL=trigmin RISE=LAST
        meas tran out0tdfall TRIG clk td=2550n VAL=trigmin RISE=2 TARG out0 VAL=trigmin FALL=LAST
        let out0tr = out0tr * 1e9
        let out0tf = out0tf * 1e9
        let out0tdrise = out0tdrise * 1e9
        let out0tdfall = out0tdfall * 1e9
        let avgi = - avgi * 1e3
        plot v(clk) v(out0)+5 v(nrst)+10
        echo "$&ixx, $&out0tr, $&out0tf, $&out0tdrise, $&out0tdfall, $&maxv, $&avgi" >> out.txt
        let ixx = ixx + step
    end
plot v(clk) v(out0)+5 v(nrst)+10
*run
* plot v(clk)+5 v(rst) v(out0)+10 v(out1)+15 v(out2)+20 
plot i(vee)
.endc

.end
