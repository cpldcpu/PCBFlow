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
Vrst nrst 0 dc 0 PULSE(5 0 500n 5n 5n 2u 80u)
Vclk clk 0 dc 0 PULSE(0 5 2u 5n 5n 4u 8u)

* Note: No pull up needed on outputs since they are internally connected. B
* Pull ups may have to be added for other designs

Xuut clk nrst out0 out1 out2 main

.tran 500p 26u
* .measure tran maxv MAX out0
* .measure tran out0tr TRIG out0 VAL=0.2*maxv RISE=1 TARG out0 VAL=0.8*maxv RISE=1

.control
let startv = 5V
let endv = 6V
let ixx = startv
let step = 1V
let pw = 0.5e-6

let freq        = 20e6
let freqstep    = freq/2   
let step = 1
let maxf = 0

echo "Step, Period [µS], f_clk [MHz], ratio_0 , ratio_1 , ratio_2 , MaxFreq [MHz], MaxV [V], AvgI [mA]" >> out.txt
    * dowhile freqclk/freq0 > 1.8
    dowhile step < 10
        alter Vcc = ixx
        let period = 1/freq
        let pw = period / 2
        alter @Vclk[pulse] = (0 5 2u 5n 5n $&pw $&period)
        
        run
        meas tran maxv MAX out0
        meas tran avgi AVG i(vcc)

        let trigmin = 0.2 * maxv 
        let trigmax = 0.5 * maxv 
        * 0.8 for RTL, 0.5 for amux

        meas tran periodclk TRIG clk td=3000n VAL=trigmax RISE=1 TARG clk td=3000n VAL=trigmax RISE=2
        meas tran period0 TRIG out0 td=3000n VAL=trigmax RISE=1 TARG out0 td=3000n VAL=trigmax RISE=2
        meas tran period1 TRIG out1 td=3000n VAL=trigmax RISE=1 TARG out1 td=3000n VAL=trigmax RISE=2
        meas tran period2 TRIG out2 td=3000n VAL=trigmax RISE=1 TARG out2 td=3000n VAL=trigmax RISE=2

        let  freqclk = 1e-6 / periodclk
        let  freq0   = 1e-6 / period0
        let  freq1   = 1e-6 / period1
        let  freq2   = 1e-6 / period2

        let ratio0   = 0.5   * freqclk/freq0
        let ratio1   = 0.25  * freqclk/freq1
        let ratio2   = 0.125 * freqclk/freq2

        let period = period * 1e6
        let avgi = - avgi * 1e3
        * plot v(clk)+5 v(nrst) v(out0)+10 v(out1)+15 v(out2)+20 

        if ratio0 > 0.95 and ratio0 < 1.05 and ratio1 >0.95 and ratio1 <1.05
            let maxf = freq / 1e6
            let freq = freq + freqstep
        else
            let freq = freq - freqstep
        end

        let freqstep = freqstep / 2

        echo "$&step, $&period, $&freqclk, $&ratio0, $&ratio1, $&ratio1, $&maxf,  $&maxv, $&avgi" >> out.txt

        let step = step + 1

    end
* plot v(clk) v(out0)+5 v(nrst)+10
*run
* plot v(clk)+5 v(nrst) v(out0)+10 v(out1)+15 v(out2)+20 
* plot i(vee)
.endc

.end

