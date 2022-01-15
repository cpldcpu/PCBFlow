
# Technologies

# RT - Bipolar Resistor Transistor Logic (default)

- "CDC6600 style RTL logic"
- High performance NOR based logic with high power consumption and medium area.
- Balanced voltage levels by using pull ups on inputs.
- Can achieve ~10 MHz with counter.vhd
- Supported gates: NOT, NOR2, NOR3, NOR4
- Flip-Flop: 
  - Latch: CDC6600-Style Polarity hold latch
  - DFF: Master-Slave DFF based on PH-Latch 
  - DFF: 6x NOR DFF
- Minimum Cell size: 0.15" x 0.25"
- Recommended components: PMBT2369, RL=3.3k, RB=3.3k, Cp=22p for 5V. 
  
Post layout simulation count.vhd:
1) PMBT2369/3.3k/3.3k/68p/ DFF6xNOR @ 5V 
   - 58 logic cells
   - Functional: Pass
   - Fmax: 25.5 MHZ @ 70.2 mA  (for RL=RB=4.7 Fmax is 19.3 MHz@49mA. with MMBT3904: 5.5 MHz)
   - clock-to-out0 delay rise: 14.3 ns fall: 14.8 ns

2) PMBT2369/3.3k/3.3k/22p/ M-S PH-Latch @ 5V
   - 69 logic cells
   - Functional: Pass
   - Fmax: 6.4 MHZ @ 79 mA
   - clock-to-out0 delay rise: 11.5 ns fall: 26.7 ns


### TODO
-   Clock distribution -> new dff has clock buffer. Manage fan out in yosys?
-   Change to 6xNOR DFF with sync reset? -> done, significant improvement in area and speed.

---

# RTPG    Bipolar Resistor Transistor Logic with pass gates

- Low speed logic optimized for low component count.
- Uses NOR style logic with additional "artistic" gates based on pass-gate NPN transistors. No voltage balancing, instead strong high level to allow fan out.
- Achieves 300-500kHz with MMBT3904 clones (e.g. CJ)
- Supported gates: NOT, NOR2, NOR3, NOR4, XOR2
- Flip-Flop: 3T master slave FF with pass gate
- Minimum cell size: 0.15" x 0.25"
- Recommended Components: MMBT3904, Rl=2.2k, Rb=10k for 5V (FOmax=4). Attention: PMBT2369 will not work in this logic style due to too low reverse beta
  
### TODO
- Implement cells with RL on output
- Clock distribution
- DFF_NP with clear
- Adopt to 0.15" y-pitch

# nmos - NMOS transistor logic

- NMOS logic based on power mosfet supporting wide number of gate types.
- Can achive 500kHz-1 MHz with counter depending on transitor type
- Supported gates: NOT, NOR2, NOR3, NAND2,NAND3, AOI2_2, AOI1_2, AOI2_2_2
- Flip-Flop: 6x NAND with clear
- Minimum cell size: 0.15" x 0.25"
- Recommended Components: 
  - low cost: 2N7002, Rl=3.3k, 
  - High speed: FNV301, Rl=2.2K
- Is very noisy on supply

### TODO

-   Move RL to output
-   Clock distribution
-   Double check DFF implementation

# LTL - LED Transistor Logic

- The bestest and fastest. Diode Transistor logic that emits light while being active.
- Can achive 500kHz-1 MHz with counter depending on transitor type
- Supported gates: NOT, NAND2,NAND3,NAND4, (AOI2_2, AOI1_2, AOI2_2_2)
- Flip-Flop: 6x NAND with clear
- Minimum cell size: 0.15" x 0.25"
- Recommended Components: 


# amux - analog multiplexer logic

### TODO
- Implement clear in DFF
- Merge both into one. 

# Deprecated

## 74LVC - 74LVC single gate logic

- Using single gate logic: 74LVC1G175 and 74LVC1G57 multi gates. Very versatile and area efficient, however 1G57 is not always easy to obtain and expensive. Rather use amux logic. Not PCB proven yet

## YG -    YG strip logic

- not finished

## NE  -    NE555 logic

- Don't use, this is more of a joke. It works, but is slow, large, expensive and power hungry.

## hybrid - hybrid nmos/bipolar logic

- Nasty logic level, neither fast nor stable. Don't use.

