# PCBFlow

Highly experimental set of scripts to transform a digital circuit described in a hardware description language (VHDL or Verilog) into a discrete transistor circuit on a PCB. (Disclaimer: I don't know what I am doing)

Makes use of:
-   GHDL
-   Yosys 
-   ABC
-   GTKView
-   NGspice
-   PCBPlace - my own placement tool written in Python
-   Freerouting (Optional)
-   Eagle (Optional)
-   EasyEDA (Optional)

Should work in a Linux shell. I am currently using WSL2. 

For details see [Project logs on HaD.io](https://hackaday.io/project/180839-vhdlverilog-to-discrete-logic-flow)

# Flow Architecture

![Flow Architecture](Images/flow_numbered.png)

The diagram above shows how the individual steps of the flow are connected. The starting point is the design (A VHDL source file) in the blue file box. In subsequent steps, this design will be transformed by various tools into new intermediate representations (grey). To aid this, technology description files and testbenches are needed (orange). The output at the end of the flow are the three green files, which describe the PCB layout (Gerber), the part list (BOM) and where the parts have to be placed on the PCB (Pick & Place).

Right now, everything is based on shell scripts that have to be invoked manually and sub-sequentially. The numbers in the process boxes indicate the number of the script that performs this step. Scripts ending on zero (10,20,30) are mandatory steps for the flow, scripts ending on other digits are optional, e.g. for intermediate simulation.

The technology description files and additional date reside in subfolders [10](10_HDL/),[20](20_SYNTH/),[30](30_PLACE/). [10](10_HDL/) also holds the design files.

Please be aware that the placement tool is in a very early experimental stage. Constants in the code may have to be tuned for better results depending on input design.

All intermediate and output files are stored in the [Work](Work/) folder. It can be cleaned by calling the "clean_all.sh" script.

The output of the automated part of the flow is an unrouted PCB. Routing and design file generation has to be invoked manually with the indicated tools. 