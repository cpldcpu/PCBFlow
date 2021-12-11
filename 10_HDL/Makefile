# VHDL Simulation workflow
# 2021-Nov-01 cpldcpu
#
# Implements the following pipeline
# 3) analyze and evaluate  VHDL source using GHDL
# 4) Run the  model using GHDL. 
# 5) Optional: Start GTKWAVE to display the output
#
# "make" - builds everything
# "make view" - builds everything and starts GTKWAVE
#
# Requires:
# - GHDL
# - GTKVIEW

VHDLFILES = counter_tb.vhd counter.vhd
TESTBENCH = testbench

# GHDL CONFIG
GHDL_CMD 		= ghdl
GHDL_FLAGS  	= --ieee=synopsys -fexplicit -Whide 
GHDL_SIM_FLAGS 	= --stop-time=100us --ieee-asserts=disable # Hide ieee library asserts 

#GTKWAVE CONFIG
GTKWAVE_CMD	 	= gtkwave.exe
GTKWAVE_FLAGS   = gtkviewsettings.gtkw --rcvar 'fontname_signals Monospace 11' --rcvar 'fontname_waves Monospace 11' # font size

.PHONY: clean

all: waveforms.ghw

work-obj93.cf: $(VHDLFILES) 
	$(GHDL_CMD) -a $(GHDL_FLAGS)  $(VHDLFILES) 
	$(GHDL_CMD) -e $(GHDL_FLAGS)  $(TESTBENCH)

waveforms.ghw: work-obj93.cf
	$(GHDL_CMD) -r $(GHDL_FLAGS)  $(TESTBENCH) $(GHDL_SIM_FLAGS) --wave=waveforms.ghw

waveforms.vcd: work-obj93.cf
	$(GHDL_CMD) -r $(GHDL_FLAGS)  $(TESTBENCH) $(GHDL_SIM_FLAGS) --vcd=waveforms.vcd

view: waveforms.ghw
# START "" gtkwave waveforms.ghw gtkviewsettings.gtkw
	$(GTKWAVE_CMD) waveforms.ghw  $(GTKWAVE_FLAGS) & 
# use the line above on linux

clean:
	rm -f *.cf *.ghw *.vcd 
