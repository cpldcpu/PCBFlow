# PCBPlace v0.2a
# 21-Nov-1 cpldcpu
#
# Very hacky early state, in urgent need of refactoring

# Needs: matplotlib, pandas, lxml

import random
import time
# import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import pandas as pd
from lxml import etree as et


# load eagle board template, insert gates, output board
class PCBPlacer():
    def __init__(self, filename):
        self.loadeagle(filename)

#load eagle file
    def loadeagle(self,filename):
        """Load eagle file """
        self.dom = et.parse(filename)
        self.n_eagle = self.dom.getroot()
        if self.n_eagle.tag != "eagle":
            raise Exception('Invalid tag name for root node - no eagle file?')
        self.n_board = self.n_eagle.find('drawing').find('board')
        self.devcounter = 100

    def saveeagle(self,filename):
        """Save eagle file """
        xml_str = et.tostring(self.dom,  xml_declaration=True, encoding="utf-8", pretty_print=True)

        f = open(filename, 'wb')
        f.write(xml_str)
        f.close()

    def addcontact(self,signal,element,pad):
        """add contact to signal if it already exists, otherwise create signal"""

        n_signals = self.n_board.find('signals')
        n_signet = n_signals.find("signal[@name='{0}']".format(signal))

        if n_signet != None:
            et.SubElement(n_signet, 'contactref', element = element, pad = pad)
        else:
            n_signet = et.SubElement(n_signals, 'signal', name = signal)
            et.SubElement(n_signet, 'contactref', element = element, pad = pad)


    # def insertNOR3(self,x, y, netin1, netin2, netin3, netout, pitch=3.8):
    #     """Insert NOR3 at position x,y
    #     Assumes inverters that can be combined to wired AND at output"""

    #     self.insertNOT(x+0*pitch,y, netin1, netout)
    #     self.insertNOT(x+1*pitch,y, netin2, netout)
    #     self.insertNOT(x+2*pitch,y, netin3, netout)

    # def insertNOR2(self,x, y, netin1, netin2, netout, pitch=3.8):
    #     """Insert NOR2 at position x,y
    #     Assumes inverters that can be combined to wired AND at output"""

    #     self.insertNOT(x+0*pitch,y, netin1, netout)
    #     self.insertNOT(x+1*pitch,y, netin2, netout)

    def insertNOT(self,x, y, netin, netout, cellname="void"):
        """Insert RTL inverter at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="RTL_components", package="SOT23", value="PMBT2369", x=str(x+1.65), y=str(y+1.4))
        et.SubElement(n_elements, 'element', name = "Rb"+cellname, library="RTL_components", package="RES0402", value="RES", x=str(x+1), y=str(y+3.4))
        et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="RTL_components", package="RES0402", value="RES", x=str(x+1), y=str(y+4.3))

        self.addcontact('GND' , "Q"+cellname, "2" )
        self.addcontact('VCC' , "Rl"+cellname, "2" )
     
        self.addcontact(netin , "Rl"+cellname, "1" )
        self.addcontact(netin , "Rb"+cellname, "1" )

        self.addcontact(netout , "Q"+cellname, "3")

        self.addcontact("B$" + str(self.devcounter), "Q"+cellname, "1")
        self.addcontact("B$" + str(self.devcounter), "Rb"+cellname, "2")

        self.devcounter += 1

    def insertNOTtap(self,x, y, netin, netbase, netout, cellname="void"):
        """Insert RTL inverter with base tap at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="RTL_components", package="SOT23", value="PMBT2369", x=str(x+1.65), y=str(y+1.4))
        et.SubElement(n_elements, 'element', name = "Rb"+cellname, library="RTL_components", package="RES0402", value="RES", x=str(x+1), y=str(y+3.4))
        et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="RTL_components", package="RES0402", value="RES", x=str(x+1), y=str(y+4.3))

        self.addcontact('GND' , "Q"+cellname, "2" )
        self.addcontact('VCC' , "Rl"+cellname, "2" )
     
        self.addcontact(netin , "Rl"+cellname, "1" )
        self.addcontact(netin , "Rb"+cellname, "1" )

        self.addcontact(netout , "Q"+cellname, "3")

        self.addcontact(netbase, "Q"+cellname, "1")
        self.addcontact(netbase, "Rb"+cellname, "2")

        self.devcounter += 1

    def insertTBUF(self,x, y, netenable, netin, netout, cellname="void"):
        """Insert RTL inverter with base tap at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="RTL_components", package="SOT23", value="PMBT2369", x=str(x+1.65), y=str(y+1.4))
        et.SubElement(n_elements, 'element', name = "Rb"+cellname, library="RTL_components", package="RES0402", value="RES", x=str(x+1), y=str(y+3.4))
        et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="RTL_components", package="RES0402", value="RES", x=str(x+1), y=str(y+4.3))
        et.SubElement(n_elements, 'element', name = "Rl2"+cellname, library="RTL_components", package="RES0402", value="RES", x=str(x+3.2), y=str(y+3.4))

        self.addcontact(netout , "Q"+cellname, "2" )
        self.addcontact('VCC' , "Rl"+cellname, "2" )
        self.addcontact('VCC' , "Rl2"+cellname, "1" )

        self.addcontact(netin , "Rl2"+cellname, "2" )

        self.addcontact(netenable , "Rl"+cellname, "1" )
        self.addcontact(netenable , "Rb"+cellname, "1" )

        self.addcontact(netin , "Q"+cellname, "3")

        self.addcontact("B$" + str(self.devcounter), "Q"+cellname, "1")
        self.addcontact("B$" + str(self.devcounter), "Rb"+cellname, "2")

        self.devcounter += 1


    def insertIO(self,x, y, netin, name =""):
        """Insert I/O pin at position x,y"""

        n_elements = self.n_board.find('elements')
        n_iopin = et.SubElement(n_elements, 'element', name = "E"+str(self.devcounter), library="RTL_components", package="1X01", value=name, x=str(x), y=str(y+2.54))
        et.SubElement(n_iopin, 'attribute', name= 'VALUE', x=str(x - 1.27), y=str(y), size="1.27", layer="27")
        self.addcontact(netin , "E"+str(self.devcounter), "1" )
        self.devcounter += 1


    def printboard(self):
        for e in self.n_board.find('elements'):
            print(e.tag)
            print(e.get('name'), e.get('value'))

        for e in self.n_board.find('signals'):
            print(e.tag)
            print(e.get('name'), e.get('value'))

class CellArray():
    def __init__(self, SizeX=0, SizeY=0 ):
        self.array = {} # Dictionariy of cells
        self.nets = {} # Dictionary of nets
        self.SizeX = SizeX
        self.SizeY = SizeY
        for y in range(SizeY):
            for x in range(SizeX):
                self.array["V"+str(x+SizeX*y)]=['EMPTY',True,x,y,[]]

    # copy content of another CellArray
    def clone(self, source):
        self.array = {} # Dictionary of cells
        self.nets = {} # Dictionary of nets
        self.SizeX = source.SizeX
        self.SizeY = source.SizeY
        self.array = deepcopy(source.array)
        self.rebuildnets()

    # output cellarray to board
    def outputtoboard(self, board, pitchx = 5, pitchy = 7):
        """ Output content of cellarray to pcb"""
     
        for key, val in self.array.items():
            celltype = val[0]
            if celltype == 'NOT':
                board.insertNOT(val[3]*pitchx,val[2]*pitchy,val[4][0],val[4][1],key)
            elif celltype == 'NOTtap':
                board.insertNOTtap(val[3]*pitchx,val[2]*pitchy,val[4][0],val[4][1],val[4][2],key)
            elif celltype == 'TBUF':
                board.insertTBUF(val[3]*pitchx,val[2]*pitchy,val[4][0],val[4][1],val[4][2],key)
            elif celltype == 'EMPTY':
                pass
            elif celltype == 'IO':
                board.insertIO(val[3]*pitchx,val[2]*pitchy,val[4][0],str(val[4][0]))
            else:
                print("Failed to insert footprint of cell {0}, type unknown\t".format(key), end="")
                print(celltype)

    # Print array content
    def printarray(self):
        ordered = sorted(self.array.items(), key=lambda item: item[1][2]+self.SizeX*item[1][3])
        columnctr = 0 
        for key, val in ordered:
#            print("{0}\t".format(val[0]), end="")
            print("{0}\t".format(key), end="")
            columnctr += 1
            if columnctr == self.SizeX:
                print()
                columnctr = 0

    # return pandas dataframe
    def returnpdframe(self):
        df=pd.DataFrame.from_dict(self.array, orient='index')
        df.columns =['Celltype','Movable','X','Y','Nets']
        return df

    # I/O cells are added to row 0 by definition for now
    def addiocell(self, net):
        for key, val in self.array.items():
            if val[0] == "EMPTY" and val[3] == 0:
#                print(key,net)
                del self.array[key]
                self.array["IO"+str(val[2])] = ['IO', False, val[2], val[3], [net]]
                return  
        print("Could not insert I/O cell!")

    # Add logic cell (subckt starting with X)
    def addlogiccell(self,name,celltype, nets):

        if celltype == "NOR2":
            self.insertcell(name+"a","NOT", [nets[0], nets[2]])
            self.insertcell(name+"b","NOT", [nets[1], nets[2]])
        elif celltype == "NOR3":
            self.insertcell(name+"a","NOT", [nets[0], nets[3]])
            self.insertcell(name+"b","NOT", [nets[1], nets[3]])
            self.insertcell(name+"c","NOT", [nets[2], nets[3]])
        elif celltype == "DFF":  # pin order: C, D, Q
            self.insertcell(name+"c","NOT", [nets[0], name+"CI"])   # clock inversion
            self.addlogiccell(name+"a","PHLATCH", [name+"CI", nets[1], name+"DI"])  # pin order: E, D, Q
            self.addlogiccell(name+"b","PHLATCH", [nets[0], name+"DI", nets[2]])  # pin order: E, D, Q
        elif celltype == "DFF7T":  # pin order: C, D, Q
            self.insertcell(name+"c","NOT", [nets[0], name+"CI"])   # clock inversion
            self.addlogiccell(name+"a","LATCH3Tn", [name+"CI", nets[1], name+"DI"])  # pin order: E, D, Q
            self.addlogiccell(name+"b","LATCH3Tn", [nets[0], name+"DI", nets[2]])  # pin order: E, D, Q
        elif celltype == "PHLATCH":  # pin order: E, D, Q
            self.insertcell(name+"I","NOT", [nets[0], name+"CI"])   # clock inversion (cannot be shared in DFF due to tpd requirements)
            self.addlogiccell(name+"X1","NOR2", [name+"CI" , nets[1]   , name+"X1o"])  # X1: D,CI,X1o
            self.addlogiccell(name+"X2","NOR2", [nets[0]   , nets[2]   , name+"X2o"])  # X2: C,Q,X2o
            self.addlogiccell(name+"X3","NOR2", [name+"X1o", name+"X2o", nets[2]   ])  # X3: X1o,X2o,Q
        elif celltype == "LATCH3Tn":  # pin order: E, D, Q
            self.addlogiccell(name+"X1","TBUF"  , [nets[0]   , nets[1]   , name+"X1o" ])   
            self.addlogiccell(name+"X2","NOTtap", [name+"X3o", name+"X1o", nets[2]    ])
            self.addlogiccell(name+"X3","NOT"   , [nets[2]   , name+"X3o"             ])    
        else:
            self.insertcell(name,celltype, nets)

    def insertcell(self,name,celltype, nets):
        for key, val in self.array.items():
            if val[0] == "EMPTY" and val[3] > 0:
#                print(name,nets)
                del self.array[key]
                self.array[name] = [celltype, True, val[2], val[3], nets]
                return  
        print("Could not insert logic cell!")

    # Add voltage source (V). These are used to shunt internal
    # signals to other signal. We will remove an internal signal for simplification

    def addshunt(self,net1,net2):
        replacenet = net1
        replacewith = net2
        for key, val in self.array.items():
            if val[0] == 'IO':
                if net1 in val[4]:
                    replacenet = net2
                    replacewith = net1
                    break
                if net2 in val[4]:
                    break
        for key, val in self.array.items():
            if val[0] == 'EMPTY':
                 continue
            self.array[key][4] = [replacewith if net==replacenet else net for net in val[4]]

    # Rebuild list of nets from cellarray
    def rebuildnets(self):
        self.nets = {}
        self.totallength = 0
        for key, val in self.array.items():
            for newnet in val[4]:
                if not newnet in self.nets:
                    self.nets[newnet]=[1e6, [key]]
                else:
                    self.nets[newnet][1].append(key)
        for key, val in self.nets.items():
            self.updatenetlength(key)
            self.totallength += self.nets[key][0]

    # Calculate the length of a specific net
    def updatenetlength(self,netname):
        if not netname in self.nets:
            print("Net not found!")
            return
        cells = self.nets[netname][1]

        if True:                     # Use half perimeter wirelength algorithm (HPWL)
            xmin, xmax = self.SizeX, 0                
            ymin, ymax = self.SizeY, 0                

            for currentcell in cells:
                xmin = xmin if self.array[currentcell][2]>xmin else self.array[currentcell][2]
                xmax = xmax if self.array[currentcell][2]<xmax else self.array[currentcell][2]
                ymin = ymin if self.array[currentcell][3]>ymin else self.array[currentcell][3]
                ymax = ymax if self.array[currentcell][3]<ymax else self.array[currentcell][3]

            netlength=2*(xmax-xmin)+ymax-ymin 
            self.nets[netname][0] = netlength
        else:                       # old algorithm, manhattan spanning tree
            lastcell = cells[-1]        
            segments = []
            for currentcell in cells:
                lenx = self.array[currentcell][2] -  self.array[lastcell][2]
                leny = self.array[currentcell][3] -  self.array[lastcell][3]
                # len = abs(lenx)  + abs(leny)  # manhattan distance
                len = abs(lenx) *3 + abs(leny)  # force routing channels
                lastcell = currentcell
                segments.append(len)
            segments.sort()
            netlength=sum(segments[:-1])  # longest segment is discarded

            self.nets[netname][0] = netlength

    # Swap two cells and update the net length selectively
    def swapcells(self, cell1, cell2):
        x1,y1 = self.array[cell1][2:4]
        x2,y2 = self.array[cell2][2:4]
        self.array[cell1][2:4] = [x2,y2]
        self.array[cell2][2:4] = [x1,y1]
        lenbefore=0
        lenafter=0
    
        for net in self.array[cell1][4]:
            lenbefore += self.nets[net][0]
            self.updatenetlength(net)
            lenafter += self.nets[net][0]
        for net in self.array[cell2][4]:
            lenbefore += self.nets[net][0]
            self.updatenetlength(net)
            lenafter += self.nets[net][0]
        self.totallength += lenafter - lenbefore
    
        # self.rebuildnets()  # suboptimal

    # Optimize by random cell swapping
    def optimizerandomexchange(self, iterations = 1000):
        for i in range(iterations):
            cell1, cell2 = random.sample(self.array.keys(),2)
            if self.array[cell1][1] == False or self.array[cell2][1] == False:
                # Don't exchange fixed cells
                continue
            oldnetlength = self.totallength
            self.swapcells(cell1,cell2)
            if self.totallength > oldnetlength:
                self.swapcells(cell1,cell2)

    # Optimize by simulated annealing
    def optimizesimulatedannealing(self, iterations = 1000, temperature = 1):
        for i in range(iterations):
            cell1, cell2 = random.sample(self.array.keys(),2)
            if self.array[cell1][1] == False or self.array[cell2][1] == False:
                # Don't exchange fixed cells
                continue
            oldnetlength = self.totallength
            self.swapcells(cell1,cell2)
            newnetlength = self.totallength
            delta=newnetlength - oldnetlength
            if delta > 0 and random.random() > np.exp(-delta / temperature):
                self.swapcells(cell1,cell2)

subckt = ""

startarray = CellArray(7,16)
#startarray = CellArray(24,48)
# startarray = CellArray(16,16)

with open("209_synthesized_output.sp", "r") as file:
# with open("synth.sp", "r") as file:
    for line in file:
        words=line.split()
        if len(words) < 1:
            continue
        if words[0] == ".SUBCKT":
            subckt = words[1]
            ports =  words[2:]
            startarray.addiocell("VCC")
            for net in ports:
                startarray.addiocell(net)
            startarray.addiocell("GND")
        elif words[0] == ".ENDS":
            subckt = ""
        elif words[0][0] == "X":
            if subckt == "":
                print("component outside of subckt", line)
                break
            else:     
                startarray.addlogiccell(words[0],words[-1],words[1:-1])
        elif words[0][0] == "V":
            if subckt == "":
                print("component outside of subckt", line)
                break
            elif words[-1] != "0" and words[-2] != DC:
                print("Voltage source is not a shunt!")
                break
            else:
                startarray.addshunt(words[1],words[2])

# Cells.printarray()
startarray.rebuildnets()
start = time.time()

pdframe = startarray.returnpdframe()
pltdata = pdframe.pivot('Y','X','Celltype')
print(pltdata)


print("Initial length:", startarray.totallength)

progress = []
temps = []



# Coarse optimization

print("Coarse optimization, picking main candidate")

coarseattempts = []

for i in range(20): # 20 coarse attempts
    array=CellArray()
    array.clone(startarray)

    random.seed(i)
    print(i)

    temp = 1000
    for _ in range (1000):
    # Cells.optimizerandomexchange(100)
        array.optimizesimulatedannealing(100,temp)
        array.rebuildnets()
        temp *=0.95
    coarseattempts.append(array)

ordered = sorted(coarseattempts, key=lambda item: item.totallength)

for len in ordered:
    print(" ",len.totallength,end='')
print()

# for len in coarseattempts:
#     print(" ",len.totallength,end='')
# print()

array_opt = ordered[0]
array_opt.rebuildnets()

print("Initial length:", array_opt.totallength)
print("Fine optimization")

random.seed(1)
temp = 1
for _ in range (10000):
    # array_opt.optimizerandomexchange(100)
    array_opt.optimizesimulatedannealing(100,temp)
    array_opt.rebuildnets()
    progress.append(array_opt.totallength)
    temps.append(temp)
    temp *=0.95
end = time.time()
# plt.subplot(311)
# plt.semilogx(progress)
# plt.grid()
# plt.subplot(312)
# plt.semilogx(temps)
# plt.grid()
# plt.subplot(313)
# plt.plot(temps,progress)
# plt.grid()
print("Elapsed time:", end-start)
print("after 100 iterations", progress[100])
# print("after 1000 iterations", progress[1000])
print("Final length:", array_opt.totallength)
# array_opt.printarray()

pdframe = array_opt.returnpdframe()
pltdata = pdframe.pivot('Y','X','Celltype')
print(pltdata)
pltdata = pdframe.pivot('Y','X','Nets')
print(pltdata)

print("Outputting board...")
pcb = PCBPlacer("../30_PLACE/board_template.brd")
array_opt.outputtoboard(pcb)
pcb.saveeagle("309_board_output.brd")

