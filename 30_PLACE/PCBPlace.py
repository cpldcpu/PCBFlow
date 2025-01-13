# PCBPlace 
# 2021/2022 www.github.com/cpldcpu
#
# Very hacky early state, in urgent need of refactoring

# Needs: numpy, pandas, lxml

from io import DEFAULT_BUFFER_SIZE
import random
import time
import sys
import math
import numpy as np
from copy import deepcopy
import pandas as pd
from lxml import etree as et
from dataclasses import dataclass

from .PCBPlacer import PCBPlacer
from .CellArray import Cell, CellArray
from .parsesptocellarray import parsesptocellarray
from .optimization import coarseoptimization, detailedoptimization
from .bufferinsertion import bufferinsertion

# ====================================================================
# Configuration area. Will be turned into commandline settings later
# ====================================================================

# !!! You need to update the lines below to adjust for your design!!! 

ArrayXwidth = 18        # This is the width of the grid and should be equal to or larger than the number of I/O pins plus two supply pins!
DesignArea  = 180        # This is the number of unit cells required for the design. It is outputted as "chip area" during the Synthesis step
                        # Fixedio fixes I/O positions within the first row. Leave empty if you want the tool to assign positions.
FixedIO     = []        # Default, tool assigns I/O
# FixedIO     = [["VCC",0,0],["GND",0,12]]
# FixedIO     =      ["VCC","inv_a", "inv_y", "xor_a", "xor_b", "xor_y", "and_a", "and_b", "and_y", "d", "clk", "q"] # for moregates.vhd

                        # Insert monitoring LEDs for I/O pins in list
LEDS        = []      # Default, don't insert any LEDs

# LEDS        = ["clk","count.0","count.1","count.2"]
# LEDS        = ["clk","dice.0","dice.1","dice.2","dice.3"]

Pullups     = []      # Default, don't insert pull up resistors
# Pullups     = ["dice.0", "dice.1" , "dice.2" , "dice.3"]      

# Optimizer settings. Only change when needed

AreaMargin = 0.2       # This is additional area that is reserved for empty cells. This value should be larger than zero to allow optimization.
                        # Too large values will result in waste of area. Default: 0.3
CoarseAttempts = 20     # Default: 20
CoarseCycles   = 1000   # Default: 1000
FineCycles     = 10000  # Default: 10000 Increase to improve larger designs. 

MaxFanOut      = 10    # Default:10  Buffers will be inserted into eligible nets with higher fanout than this

# Pitch of grid on PCB in mm

PCBPitchx = 2.54*1.5 # LTL
PCBPitchy = 2.54*2.5 # 

# PCBPitchx = 2.54*2 # default 2*2.54
# PCBPitchy = 2.54*3 # default 3*2.54

# PCBPitchx = 2.54*3 # NE555 logic
# PCBPitchy = 2.54*4 # 

# File names. Don't touch unless you want to modify the flow

InputFileName       = "209_synthesized_output.sp"
PCBTemplateFile     = "../30_PLACE/board_template.brd" 
PCBOutputFile       = "309_board_output.brd"
SpiceOutputFile     = "308_extracted_netlist.sp"
FanoutOutputFile    = "307_fanout.txt"
NetsOutputFile      = "306_nets.csv"
PlacementOutputFile = "305_placement.csv"

# =========== START OF MAIN ===============================

print("=== Setting up array ===\n")

startarray = CellArray(ArrayXwidth,1+int(math.ceil(DesignArea*(1+AreaMargin)/ArrayXwidth)))

print("Number of cells in design: {0}\nArea margin: {1}%".format(DesignArea,AreaMargin*100))
print("Array Xwidth: {0}\nArray Ywidth: {1}\n".format(startarray.SizeX, startarray.SizeY))

print("=== Parsing input file & Inserting Microcells ===\n")

startarray.addfixediocells(FixedIO) # Add fixed IO cells if there are any
parsesptocellarray(InputFileName,startarray,FixedIO,LEDS,Pullups)

print("Parsing successful...")
print()

print("=== Peephole optimizations ===\n")

startarray.peepholeoptimizer()
print()
print("=== Initial placement ===\n")

startarray.rebuildnets()
print("Initial net-length:", startarray.totallength)
print("Initial Placement:\n")

pdframe = startarray.returnpdframe()
pltdata = pdframe.pivot(index='Y',columns='X',values='Celltype')
print(pltdata)
print()

print("=== Coarse optimization, picking main candidate ===\n")

startarray.optimizationrules([5,1.0,1])

start = time.time()
array_opt=coarseoptimization(startarray, attempts=CoarseAttempts, optimizationcycles=CoarseCycles)
array_opt.rebuildnets()  # just to be sure
end = time.time()
print("Elapsed time: {0:6.3f}s\n".format(end-start))

print("=== Candidate Placement ===\n")

pdframe = array_opt.returnpdframe()
pltdata = pdframe.pivot(index='Y',columns='X',values='Celltype')
print(pltdata)

print("=== Detailed optimization ===\n")

array_opt.optimizationrules([20,2.5,1])

print("Initial length:", array_opt.totallength)

start = time.time()
array_opt=detailedoptimization(array_opt, optimizationcycles=FineCycles)
array_opt.rebuildnets()  # just to be sure
end = time.time()

print("Final length:", array_opt.totallength)
print("Elapsed time: {0:6.3f}s".format(end-start))
print()
# array_opt.printarray()

print("=== Buffer insertion ===\n")

start = time.time()
buffercellsused = False

for netkey, data in array_opt.nets.items():
    if len(data[1])>MaxFanOut:
        if bufferinsertion(array_opt, netkey,maxfo=MaxFanOut):
            buffercellsused = True

array_opt.rebuildnets()
end = time.time()

print("Elapsed time: {0:6.3f}s".format(end-start))
print()

if buffercellsused:
    print("=== Optimizing buffer cell placement ===\n")
    array_opt.optimizationrules([20,2.5,1])
    print("Initial length:", array_opt.totallength)

    start = time.time()
    array_opt=detailedoptimization(array_opt, optimizationcycles=FineCycles)
    array_opt.rebuildnets()  # just to be sure
    end = time.time()

    print("Final length:", array_opt.totallength)
    print("Elapsed time: {0:6.3f}s".format(end-start))
    print()
# array_opt.printarray()
else:
    print("No buffer cells inserted\n")

print("=== Final Placement ===\n")

pdframe = array_opt.returnpdframe()
# pltdata = pdframe.pivot('Y','X','Celltype')
# print(pltdata)
pltdata = pdframe.pivot(index='Y',columns='X',values='Celltype')
print(pltdata)
pltdata.to_csv(PlacementOutputFile, sep='\t')

print("\nMicrocell counts:")
microcells=pdframe['Celltype'].value_counts()
print(microcells)

microcelldict=microcells.to_dict()
del microcelldict["IO"]
del microcelldict["EMPTY"]
print(f"\nTotal area usage by logic cells: {sum(microcelldict.values())}\n")

print("\n=== Final Nets ===\n")

pltdata = pdframe.pivot(index='Y',columns='X',values='Nets')
# print(pltdata)
pltdata.to_csv(NetsOutputFile, sep='\t')

with open(FanoutOutputFile, "w") as file:
    for key, net in sorted(array_opt.nets.items(), key=lambda x: len(x[1][1]), reverse = True):
        file.write("{0}\t{1}\t{2}\n".format(key,len(net[1])-1,net[1]))

# array_opt.printnets()

print("\n=== Writing Footprints to File ===\n")
pcb = PCBPlacer(PCBTemplateFile)
array_opt.outputtoboard(pcb, pitchx = PCBPitchx, pitchy = PCBPitchy )
pcb.saveeagle(PCBOutputFile)

print("\n=== Writing Extracted Spice Netlist ===\n")

array_opt.extracttospice(SpiceOutputFile)

print("\n=== Component usage ===\n")

print("{0:20}{1}\n".format("Component","Count"))
compcount=0
for key, num in pcb.components.items():
    print("{0:20}{1}".format(key,num))
    compcount += num

print("{0:20}{1}".format("------------------","-----"))
print("{0:20}{1}".format("Total:",compcount))
