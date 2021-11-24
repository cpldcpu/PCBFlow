# PCBPlace v0.3a
# 21-Nov-23 cpldcpu
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


# load eagle board template, insert gates, output board
class PCBPlacer():
    def __init__(self, filename):
        self.loadeagle(filename)
        self.components= {}    # Dictionary of components

    def countcomponent(self, componentname, number=1):
        if not componentname in self.components:
            self.components[componentname] = number
        else:
            self.components[componentname] += number

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

        if n_signet == None:  # Signal does not exist yet
            n_signet = et.SubElement(n_signals, 'signal', name = signal)

            if signal=="VCC" or signal=="GND":   
                n_signet.set("class","1")   # Define as power net

        et.SubElement(n_signet, 'contactref', element = element, pad = pad)

    def insertLED(self,x, y, netin, cellname="void"):
        """Insert LED including bipolar driver transistor"""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23", value="PMBT2369", x=str(x+1.65), y=str(y+1.4))
        et.SubElement(n_elements, 'element', name = "Rb"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+3.4))
        et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+4.3))
        et.SubElement(n_elements, 'element', name = "L"+cellname, library="discrete_logic_components", package="LED0603", value="RES", x=str(x+3.25), y=str(y+3.4) ,rot="R180")
        self.countcomponent("npn transistor")
        self.countcomponent("resistor",2)
        self.countcomponent("led")

        self.addcontact('GND' , "Q"+cellname, "2" )
        self.addcontact("B$" + str(self.devcounter) , "Rl"+cellname, "2" )
        self.addcontact("B$" + str(self.devcounter) , "L"+cellname, "A" )
     
        self.addcontact('VCC' , "Rl"+cellname, "1" )

        self.devcounter += 1

        self.addcontact(netin , "Rb"+cellname, "1" )

        self.addcontact("B$" + str(self.devcounter) , "Q"+cellname, "3")
        self.addcontact("B$" + str(self.devcounter) , "L"+cellname, "C")

        self.devcounter += 1

        self.addcontact("B$" + str(self.devcounter), "Q"+cellname, "1")
        self.addcontact("B$" + str(self.devcounter), "Rb"+cellname, "2")

        self.devcounter += 1

    def insertNOT(self,x, y, netin, netout, cellname="void"):
        """Insert RTL inverter at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        self.insertNOTb(x,y,netin, "B$" + str(self.devcounter), netout, cellname)
        self.devcounter += 1

    def insertNOTb(self,x, y, netin, netbase, netout, cellname="void"):
        """Insert RTL inverter with base tap at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23", value="PMBT2369", x=str(x+1.65), y=str(y+1.4))
        et.SubElement(n_elements, 'element', name = "Rb"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+3.4))
        et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+4.3))
        self.countcomponent("npn transistor")
        self.countcomponent("resistor",2)

        self.addcontact('GND' , "Q"+cellname, "2" )
        self.addcontact('VCC' , "Rl"+cellname, "2" )
     
        self.addcontact(netin , "Rl"+cellname, "1" )
        self.addcontact(netin , "Rb"+cellname, "1" )

        self.addcontact(netout , "Q"+cellname, "3")

        self.addcontact(netbase, "Q"+cellname, "1")
        self.addcontact(netbase, "Rb"+cellname, "2")

        self.devcounter += 1



    def insertTBUFe(self,x, y, netenable, netin, netout, cellname="void"):
        """Insert RTL inverter with base tap at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23", value="PMBT2369", x=str(x+1.65), y=str(y+1.4))
        et.SubElement(n_elements, 'element', name = "Rb"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+3.4))
        et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+4.3))
        et.SubElement(n_elements, 'element', name = "Rl2"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+3.2), y=str(y+3.4))
        self.countcomponent("npn transistor")
        self.countcomponent("resistor",3)

        self.addcontact(netin , "Q"+cellname, "2" )
        self.addcontact('VCC' , "Rl"+cellname, "2" )
        self.addcontact('VCC' , "Rl2"+cellname, "1" )

        self.addcontact(netin , "Rl2"+cellname, "2" )

        self.addcontact(netenable , "Rl"+cellname, "1" )
        self.addcontact(netenable , "Rb"+cellname, "1" )

        self.addcontact(netout , "Q"+cellname, "3")

        self.addcontact("B$" + str(self.devcounter), "Q"+cellname, "1")
        self.addcontact("B$" + str(self.devcounter), "Rb"+cellname, "2")

        self.devcounter += 1        

    def insertTBUFc(self,x, y, netenable, netin, netout, cellname="void"):
        """Insert RTL inverter with base tap at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23", value="PMBT2369", x=str(x+1.65), y=str(y+1.4))
        et.SubElement(n_elements, 'element', name = "Rb"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+3.4))
        et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+4.3))
        et.SubElement(n_elements, 'element', name = "Rl2"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+3.2), y=str(y+3.4))
        self.countcomponent("npn transistor")
        self.countcomponent("resistor",3)

        self.addcontact(netin , "Q"+cellname, "3" )
        self.addcontact('VCC' , "Rl"+cellname, "2" )
        self.addcontact('VCC' , "Rl2"+cellname, "1" )

        self.addcontact(netin , "Rl2"+cellname, "2" )

        self.addcontact(netenable , "Rl"+cellname, "1" )
        self.addcontact(netenable , "Rb"+cellname, "1" )

        self.addcontact(netout , "Q"+cellname, "2")

        self.addcontact("B$" + str(self.devcounter), "Q"+cellname, "1")
        self.addcontact("B$" + str(self.devcounter), "Rb"+cellname, "2")

        self.devcounter += 1        


    def insertNMOSinv(self,x, y, netin, netdrain, netsource, cellname="void"):
        """Insert NMOS inverter with base tap at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23", value="2N7002", x=str(x+1.65), y=str(y+1.4))
        et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+3.4))
        self.countcomponent("nmos transistor")
        self.countcomponent("resistor")

        self.addcontact(netsource , "Q" +cellname, "2" )
        self.addcontact('VCC'     , "Rl"+cellname, "2" )
     
        self.addcontact(netin     , "Rl"+cellname, "1" )
        self.addcontact(netin     , "Q" +cellname, "1")

        self.addcontact(netdrain , "Q"  +cellname, "3")

        self.devcounter += 1

    def insertNMOSinvg(self,x, y, netin, netgate, netdrain, cellname="void"):
        """Insert nmos inverter with Gate tap at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23", value="2N7002", x=str(x+1.65), y=str(y+1.4))
        et.SubElement(n_elements, 'element', name = "Rb"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+3.4))
        et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+4.3))
        self.countcomponent("nmos transistor")
        self.countcomponent("resistor",2)

        self.addcontact('GND'   , "Q"+cellname , "2" )
        self.addcontact('VCC'   , "Rl"+cellname, "2" )
     
        self.addcontact(netin   , "Rl"+cellname, "1" )
        self.addcontact(netin   , "Rb"+cellname, "1" )

        self.addcontact(netdrain, "Q"+cellname , "3")

        self.addcontact(netgate , "Q"+cellname , "1")
        self.addcontact(netgate , "Rb"+cellname, "2")


    def insertAMUX(self,x, y, netB1, netB2, netS, netout, cellname=""):
        """Insert analog multiplexer 74LVC1G3157
        Assumes standard library, supply nets VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SC70-6", value="74LVC1G3157", x=str(x+1.65), y=str(y+1.4))
        self.countcomponent("amux")

        self.addcontact(netB2  , "Q"+cellname, "1" )
        self.addcontact('GND'  , "Q"+cellname, "2" )
        self.addcontact(netB1  , "Q"+cellname, "3" )
        self.addcontact(netout , "Q"+cellname, "4" )
        self.addcontact('VCC'  , "Q"+cellname, "5" )
        self.addcontact(netS   , "Q"+cellname, "6" )

    def insert1G57(self,x, y, netina, netinb, netinc, netout, cellname=""):
        """Insert multifunction gate 74LVC1G57
        Assumes standard library, supply nets VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23-6", value="74LVC1G57", x=str(x+1.65), y=str(y+1.4))
        self.countcomponent("1G57")

        self.addcontact(netinb , "Q"+cellname, "1" )
        self.addcontact('GND'  , "Q"+cellname, "2" )
        self.addcontact(netina , "Q"+cellname, "3" )
        self.addcontact(netout , "Q"+cellname, "4" )
        self.addcontact('VCC'  , "Q"+cellname, "5" )
        self.addcontact(netinc , "Q"+cellname, "6" )

    def insert1G175(self,x, y, netclk, netind, netclrn, netoutq, cellname=""):
        """Insert D-Flipflop 74LVC1G175
        Assumes standard library, supply nets VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23-6", value="74LVC1G175", x=str(x+1.65), y=str(y+1.4))
        self.countcomponent("1G175")

        self.addcontact(netclk  , "Q"+cellname, "1" )
        self.addcontact('GND'   , "Q"+cellname, "2" )
        self.addcontact(netind  , "Q"+cellname, "3" )
        self.addcontact(netoutq , "Q"+cellname, "4" )
        self.addcontact('VCC'   , "Q"+cellname, "5" )
        self.addcontact(netclrn , "Q"+cellname, "6" )

    def insertIO(self,x, y, netin, name =""):
        """Insert I/O pin at position x,y"""

        n_elements = self.n_board.find('elements')
        n_iopin = et.SubElement(n_elements, 'element', name = "E"+str(self.devcounter), library="discrete_logic_components", package="1X01", value=name, x=str(x), y=str(y+2.54))
#        et.SubElement(n_iopin, 'attribute', name= 'VALUE', x=str(x - 1.27), y=str(y), size="1.27", layer="27") # adds name to document layer

        self.countcomponent("pin")

        self.addcontact(netin , "E"+str(self.devcounter), "1" )
        self.devcounter += 1

        # Add pin name to tPlace layer so it shows up on the silk screen
        n_plain = self.n_board.find('plain')
        if n_plain == None:
            n_plain = et.SubElement(self.n_board, 'plain')

        n_text = et.SubElement(n_plain, 'text', layer='21', size='1.27', x=str(x-1.27), y=str(y-0.5))
        n_text.text = name

    def printboard(self):
        for e in self.n_board.find('elements'):
            print(e.tag)
            print(e.get('name'), e.get('value'))

        for e in self.n_board.find('signals'):
            print(e.tag)
            print(e.get('name'), e.get('value'))

class CAParsingError(Exception):
    pass

# Define data structure of cell
@dataclass
class Cell:
    type:        str
    moveable:    bool
    x:           int
    y:           int
    pin:         list
class CellArray():
    def __init__(self, SizeX=0, SizeY=0 ):
        self.array = {} # Dictionary of cells
        self.nets = {} # Dictionary of nets
        self.SizeX = SizeX
        self.SizeY = SizeY
        for y in range(SizeY):
            for x in range(SizeX):
                self.array["V"+str(x+SizeX*y)]=Cell('EMPTY',True,x,y,[])

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
            # celltype = val[0]
            celltype = val.type
        ## RTL cells            
            if celltype == 'NOT':
                board.insertNOT(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],key)
            elif celltype == 'NOTb':
                board.insertNOTb(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)
            elif celltype == 'TBUFe':    # TBUF as part of latch
                board.insertTBUFe(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)
            elif celltype == 'TBUFc':    # TBUF as part of latch
                board.insertTBUFc(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)
 #           elif celltype == '__TBUF_':   # TBUF as synthesized by Yosys - TODO: double check pin assignment!
 #               board.insertTBUF(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)
        ## Amux logic cells
            elif celltype == 'AMUX':
                board.insertAMUX(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],val.pin[3],key)
        ## LVC logic cells
        #   def insert1G175(self,x, y, netclk, netind, netclrn, netoutq, cellname=""):
        #   def insert1G57 (self,x, y, netina, netinb, netinc , netout , cellname=""):
            elif celltype == 'LVC1G175':
                board.insert1G175(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],val.pin[3],key)
            elif celltype == 'LVC1G57':                
                board.insert1G57(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],val.pin[3],key)
        # nmos cells
            elif celltype == 'NM':                
                board.insertNMOSinv(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)
        # hybrid cells
            elif celltype == 'NMg':
                board.insertNMOSinvg(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)
        ## Generic cells
            elif celltype == 'EMPTY':
                pass            
            elif celltype == 'IO':
                board.insertIO(val.y*pitchx,val.x*pitchy,val.pin[0],str(val.pin[0]))
        # LED
            elif celltype == 'LED':
                board.insertLED(val.y*pitchx,val.x*pitchy,val.pin[0],key)
            else:
                print("Failed to insert footprint of cell {0}, type unknown\t".format(key), end="")
                print(celltype)

    def extracttospice(self, filename):
        """Output current cellarray to spicelist (post layout extraction)"""
        with open(filename, "w") as file:

            file.writelines("* Extracted Spice Netlist Generated by PCBPlace.py *\n\n")
            # I/O Pins (Extracted in order of insertion, VCC GND omitted)
            file.write(".SUBCKT main")
            for key, val in self.array.items():
                if  val.type == "IO" and val.pin[0] != "VCC" and val.pin[0] != "GND":
                    file.write(" "+val.pin[0])
            file.write("\n")
            # Cells
            for key, val in self.array.items():
                if  val.type != "IO" and val.type != "EMPTY":
                    file.write(key)
                    for net in val.pin:
                        file.write(" "+net)
                    file.write(" "+val.type+"\n")
            file.writelines(".ENDS main\n")
        return

    # Output 
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

    def printnets(self):
        """ list all nets with fanout"""
        for key, net in self.nets.items():
            print("Net: {0:20}Connections: {1}".format(key,len(net[1])))

    # return pandas dataframe
    def returnpdframe(self):
        df=pd.DataFrame.from_dict(self.array, orient='index')
        df.columns =['Celltype','Movable','X','Y','Nets']
        return df

    # I/O cells are added to row 0 by definition for now
    def addiocell(self, net,FixedIO=[],LEDS=[]):
        for key, val in self.array.items():
            if val.type == "EMPTY" and val.y == 0:
                if net in FixedIO:
                    if val.x==FixedIO.index(net):
                        del self.array[key]
                        self.array["IO"+str(val.x)] = Cell('IO', False, val.x, val.y, [net])
                        if net in LEDS:
                            self.addled(net,val.x,val.y+1)
                        return
                elif val.x>=len(FixedIO):
                    del self.array[key]
                    self.array["IO"+str(val.x)] = Cell('IO', False, val.x, val.y, [net])
                    if net in LEDS:
                        self.addled(net,val.x,val.y+1)
                    return  
        raise CAParsingError("Could not insert I/O cell in line zero! Please increase the X-width of the cell array or correct FixedIO assignment.")

    def addled(self, net , x , y ):
        """ add LED at fixed position"""
        for key, val in self.array.items():
            if val.type == "EMPTY" and val.x == x and val.y == y:
                del self.array[key]
                self.array["XLED"+str(val.x)] = Cell('LED', False, val.x, val.y, [net])                
                return
        raise CAParsingError("Could not insert LED cell for NET: "+str(net))
        

    # Add logic cell (subckt starting with X)
    # Complex cells are recursively broken down into less complex cells
    def addlogiccell(self,name,celltype, nets):

        # RTL cells
        if celltype == "NOR2":
            self.insertcell(name+"a","NOT", [nets[0], nets[2]])
            self.insertcell(name+"b","NOT", [nets[1], nets[2]])
        elif celltype == "NOR3":
            self.insertcell(name+"a","NOT", [nets[0], nets[3]])
            self.insertcell(name+"b","NOT", [nets[1], nets[3]])
            self.insertcell(name+"c","NOT", [nets[2], nets[3]])
        elif celltype == "XOR2":  
            self.addlogiccell(name+"a","TBUFe" , [nets[0]   , nets[1]   , name+"x" ])   
            self.addlogiccell(name+"b","TBUFe" , [nets[1]   , nets[0]   , name+"x" ])   
            self.addlogiccell(name+"c","NOT"   , [name+"x"  , nets[2]] ) 
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
            self.addlogiccell(name+"X1","TBUFc" , [nets[0]   , nets[1]   , name+"X1o" ])   
            self.addlogiccell(name+"X2","NOTb"  , [name+"X3o", name+"X1o", nets[2]    ])
            self.addlogiccell(name+"X3","NOT"   , [nets[2]   , name+"X3o"             ])    
        # AMUX cells
        # insertAMUX(self,x, y, netB1, netB2,  netS, netout, cellname=""):
        elif celltype == "am_NOT":
            self.insertcell(name+"" ,"AMUX", ['VCC'   , 'GND'   , nets[0] , nets[1] ])
        elif celltype == "am_AND2":
            self.insertcell(name+"" ,"AMUX", ['GND'   , nets[1] , nets[0] , nets[2] ])
        elif celltype == "am_ANDN2":
            self.insertcell(name+"" ,"AMUX", [nets[1] , 'GND'   , nets[0] , nets[2] ])
        elif celltype == "am_OR2":
            self.insertcell(name+"" ,"AMUX", [nets[1] , 'VCC'   , nets[0] , nets[2] ])
        elif celltype == "am_ORN2":
            self.insertcell(name+"" ,"AMUX", ['VCC'   , nets[1] , nets[0] , nets[2] ])
        elif celltype == "am_MUX2":
            self.insertcell(name+"" ,"AMUX", [nets[0] , nets[1] , nets[2] , nets[3] ])
        elif celltype == "am_XOR2":
            self.addlogiccell(name+"a","am_NOT", [nets[1] , name+"Bn"])   
            self.insertcell  (name+"b","AMUX"  , [nets[1] , name+"Bn" , nets[0] , nets[2] ])
        elif celltype == "am_XNOR2":
            self.addlogiccell(name+"a","am_NOT", [nets[1]  , name+"Bn"])   
            self.insertcell  (name+"b","AMUX"  , [name+"Bn", nets[1]  , nets[0] , nets[2] ])
        elif celltype == "am_DFF":
            # 5 amux latch
            # self.addlogiccell(name+"c","am_NOT",   [nets[0], name+"CI"])   # clock inversion    
            # self.addlogiccell(name+"a","am_LATCH", [name+"CI", nets[1], name+"DI"])  # pin order: E, D, Q
            # self.addlogiccell(name+"b","am_LATCH", [nets[0], name+"DI", nets[2]])  # pin order: E, D, Q
            # 4 amux latch according to Joan Illuchs idea. a bit more timing critical, but seems to work in spice.
            self.addlogiccell(name+"a","am_LATCH_nClk", [nets[0], nets[1], name+"DI"])  # pin order: E, D, Q
            self.addlogiccell(name+"b","am_LATCH", [nets[0], name+"DI", nets[2]])  # pin order: E, D, Q
        elif celltype == "am_LATCH":
            self.insertcell(name+"a" ,"AMUX", [nets[2] , nets[1] , nets[0]    , name+"X1o" ])
            self.insertcell(name+"b" ,"AMUX", [ 'GND'  , 'VCC'   , name+"X1o" , nets[2]    ])
        elif celltype == "am_LATCH_nClk":  # negatived Enable/clock input
            self.insertcell(name+"a" ,"AMUX", [nets[1] , nets[2] , nets[0]    , name+"X1o" ])
            self.insertcell(name+"b" ,"AMUX", [ 'GND'  , 'VCC'   , name+"X1o" , nets[2]    ])
        # LVC cells
        # insert1G175(self,x, y, netclk, netind, netclrn, netoutq, cellname=""):
        # insert1G57 (self,x, y, netina, netinb, netinc , netout , cellname=""):
        elif celltype == "lvc_DFF":
            self.insertcell(name ,"LVC1G175", [nets[0] , nets[1] , "VCC"   , nets[2] ])
        elif celltype == "lvc_DFF_clear":
            self.insertcell(name ,"LVC1G175", [nets[0] , nets[1] , nets[2] , nets[3] ])
        elif celltype == "lvc_NOT":
            self.insertcell(name ,"LVC1G57",  [nets[0] , "GND"   , "GND"   , nets[1] ])
        elif celltype == "lvc_NOR2":
            self.insertcell(name ,"LVC1G57",  [nets[0] , "GND"   , nets[1] , nets[2] ])
        elif celltype == "lvc_AND2":
            self.insertcell(name ,"LVC1G57",  ["VCC"   , nets[0] , nets[1] , nets[2] ])
        elif celltype == "lvc_SZ57":
            self.insertcell(name ,"LVC1G57",  [nets[0] , nets[1] , nets[2] , nets[3] ])
        elif celltype == "lvc_NNAND2":
            self.insertcell(name ,"LVC1G57",  ["GND"   , nets[0] , nets[1] , nets[2] ])
        elif celltype == "lvc_XNOR2":
            self.insertcell(name ,"LVC1G57",  [nets[0] , nets[0] , nets[1] , nets[2] ])
        # nmos cells
        #   def insertNMOSinv(self,x, y, netin, netdrain, netsource, cellname="void"):
        elif celltype == "nm_NOT":
            self.insertcell(name ,"NM"        ,   [nets[0] , nets[1]  , "GND"    ])
        elif celltype == "nm_NAND2":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[2]  , name+"x" ])
            self.insertcell(name+"b" ,"NM"    ,   [nets[1] , name+"x" , "GND"    ])
        elif celltype == "nm_NAND3":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[3]  , name+"x" ])
            self.insertcell(name+"b" ,"NM"    ,   [nets[1] , name+"x" , name+"v" ])
            self.insertcell(name+"c" ,"NM"    ,   [nets[2] , name+"v" , "GND"    ])
        elif celltype == "nm_NOR2":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[2]  , "GND"    ])
            self.insertcell(name+"b" ,"NM"    ,   [nets[1] , nets[2]  , "GND"    ])
        elif celltype == "nm_NOR3":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[3]  , "GND"    ])
            self.insertcell(name+"b" ,"NM"    ,   [nets[1] , nets[3]  , "GND"    ])
            self.insertcell(name+"c" ,"NM"    ,   [nets[2] , nets[3]  , "GND"    ])
        elif celltype == "nm_AOI2_2":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[4]  , name+"x" ])
            self.insertcell(name+"b" ,"NM"    ,   [nets[1] , name+"x" , "GND"    ])
            self.insertcell(name+"c" ,"NM"    ,   [nets[2] , nets[4]  , name+"v" ])
            self.insertcell(name+"d" ,"NM"    ,   [nets[3] , name+"v" , "GND"    ])
        elif celltype == "nm_AOI2_2_2":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[6]  , name+"x" ])
            self.insertcell(name+"b" ,"NM"    ,   [nets[1] , name+"x" , "GND"    ])
            self.insertcell(name+"c" ,"NM"    ,   [nets[2] , nets[6]  , name+"v" ])
            self.insertcell(name+"d" ,"NM"    ,   [nets[3] , name+"v" , "GND"    ])
            self.insertcell(name+"e" ,"NM"    ,   [nets[4] , nets[6]  , name+"u" ])
            self.insertcell(name+"f" ,"NM"    ,   [nets[5] , name+"u" , "GND"    ])
        elif celltype == "nm_AOI1_2":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[3] , "GND"    ])
            self.insertcell(name+"b" ,"NM"    ,   [nets[1] , nets[3]  , name+"x" ])
            self.insertcell(name+"c" ,"NM"    ,   [nets[2] , name+"x" , "GND"    ])
        elif celltype == "nm_DFF":  # pin order: C, D, Q
            self.addlogiccell(name+"c","nm_NOT"    , [nets[0], name+"CI"])   # clock inversion
            self.addlogiccell(name+"a","nm_PHLATCH", [name+"CI", nets[1], name+"DI"])  # pin order: E, D, Q
            self.addlogiccell(name+"b","nm_PHLATCH", [nets[0], name+"DI", nets[2]])  # pin order: E, D, Q
            # self.addlogiccell(name+"a","nm_5TLATCH", [name+"CI", nets[1], name+"DI"])  # pin order: E, D, Q
            # self.addlogiccell(name+"b","nm_5TLATCH", [nets[0], name+"DI", nets[2]])  # pin order: E, D, Q
        elif celltype == "nm_PHLATCH":  # pin order: E, D, Q
            self.addlogiccell(name+"I" ,"nm_NOT" , [nets[0], name+"CI"])   # clock inversion (cannot be shared in DFF due to tpd requirements)
            self.addlogiccell(name+"X1","nm_NOR2", [name+"CI" , nets[1]   , name+"X1o"])  # X1: D,CI,X1o
            self.addlogiccell(name+"X2","nm_NOR2", [nets[0]   , nets[2]   , name+"X2o"])  # X2: C,Q,X2o
            self.addlogiccell(name+"X3","nm_NOR2", [name+"X1o", name+"X2o", nets[2]   ])  # X3: X1o,X2o,Q
        # Experimental 5T PH Latch. Requires tuning gate speeds, which does not work in this framework
        # elif celltype == "nm_5TLATCH":  # pin order: E, D, Q            
        #     self.addlogiccell(name+"X1","nm_NOR2" ,[nets[0]      , nets[2]   , name+"X1o"])  
        #     self.addlogiccell(name+"X2","nm_AOI1_2",[name+"X1o"   , nets[0]   , nets[1]  ,  nets[2]])  
        # Hybrid gates (bipolar pass gate + nmos )
        #     def insertTBUF(self,x, y, netenable, netin, netout, cellname="void"):
        #     def insertNMOSinvg(self,x, y, netin, netgate, netdrain, cellname="void"):

        elif celltype == "hy_XOR2":  
            self.addlogiccell(name+"a","TBUFe" , [nets[0]   , nets[1]   , name+"x" ])   
            self.addlogiccell(name+"b","TBUFe" , [nets[1]   , nets[0]   , name+"x" ])   
            self.addlogiccell(name+"c","nm_NOT", [name+"x"  , nets[2]] ) 
        elif celltype == "hy_DFF7T":  # pin order: C, D, Q
            self.addlogiccell(name+"c","nm_NOT", [nets[0], name+"CI"])   # clock inversion
            self.addlogiccell(name+"a","hy_LATCH3Tn", [name+"CI", nets[1], name+"DI"])  # pin order: E, D, Q
            self.addlogiccell(name+"b","hy_LATCH3Tn", [nets[0], name+"DI", nets[2]])  # pin order: E, D, Q
        elif celltype == "hy_LATCH3Tn":  # pin order: E, D, Q
            self.addlogiccell(name+"X1","TBUFe" , [nets[0]   , nets[1]   , name+"X1o" ])   
            self.addlogiccell(name+"X2","NMg"   , [name+"X3o", name+"X1o", nets[2]    ])
            self.addlogiccell(name+"X3","nm_NOT", [nets[2]   , name+"X3o"             ])    

        else:
            self.insertcell(name,celltype, nets)

    def insertcell(self,name,celltype, nets):
        for key, val in self.array.items():
            if val.type == "EMPTY" and val.y > 0:
#                print(name,nets)
                del self.array[key]
                self.array[name] = Cell(celltype, True, val.x, val.y, nets)
                return
        raise CAParsingError("Failure to insert Cell. Cell array size too small for design! Increase number of cells.")

    # Add voltage source (V). These are used to shunt internal
    # signals to other signal. We will remove an internal signal for simplification

    def addshunt(self,net1,net2):
        replacenet = net1
        replacewith = net2
        for key, val in self.array.items():
            if val.type == 'IO':
                if net1 in val.pin:
                    replacenet = net2
                    replacewith = net1
                    break
                if net2 in val.pin:
                    break
        for key, val in self.array.items():     # TODO: #1 Introduce handling of shunting more than one I/O pin to internal net
            if val.type == 'EMPTY':
                 continue
            self.array[key].pin = [replacewith if net==replacenet else net for net in val.pin]

    # Rebuild list of nets from cellarray
    def rebuildnets(self):
        self.nets = {}
        self.totallength = 0
        for key, val in self.array.items():
            # for newnet in val[4]:
            for newnet in val.pin:
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
                xmin = xmin if self.array[currentcell].x>xmin else self.array[currentcell].x
                xmax = xmax if self.array[currentcell].x<xmax else self.array[currentcell].x
                ymin = ymin if self.array[currentcell].y>ymin else self.array[currentcell].y
                ymax = ymax if self.array[currentcell].y<ymax else self.array[currentcell].y

            netlength=3*(xmax-xmin)+ymax-ymin 
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
        x1,y1 = [self.array[cell1].x , self.array[cell1].y]
        x2,y2 = [self.array[cell2].x , self.array[cell2].y]
        [self.array[cell1].x , self.array[cell1].y] = [x2,y2]
        [self.array[cell2].x , self.array[cell2].y] = [x1,y1]
        lenbefore=0
        lenafter=0
    
        for net in self.array[cell1].pin:
            lenbefore += self.nets[net][0]
            self.updatenetlength(net)
            lenafter += self.nets[net][0]
        for net in self.array[cell2].pin:
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
            if self.array[cell1].moveable == False or self.array[cell2].moveable == False:
                # Don't exchange fixed cells
                continue
            oldnetlength = self.totallength
            self.swapcells(cell1,cell2)
            newnetlength = self.totallength
            delta=newnetlength - oldnetlength
            if delta > 0 and random.random() > np.exp(-delta / temperature):
                self.swapcells(cell1,cell2)


def parsesptocellarray(filename, startarray,FixedIO=[],LEDS=[]):
    """ Parse a spice netlist given as file to a CellArray structure    
    filename = name of spice netlist
    inputarray = CellArray 
    """
    subckt = ""
    with open(filename, "r") as file:
    # with open("synth.sp", "r") as file:
        for line in file:
            try:
                words=line.split()
                if len(words) < 1:
                    continue
                if words[0] == ".SUBCKT":
                    subckt = words[1]
                    ports =  words[2:]
                    startarray.addiocell("VCC", FixedIO)
                    for net in ports:
                        startarray.addiocell(net, FixedIO,LEDS)
                    startarray.addiocell("GND", FixedIO)
                elif words[0] == ".ENDS":
                    subckt = ""
                elif words[0][0] == "X":
                    if subckt == "":                    
                        raise CAParsingError("component outside of subckt")
                    else:     
                        startarray.addlogiccell(words[0],words[-1],words[1:-1])
                elif words[0][0] == "V":
                    if subckt == "":
                        raise CAParsingError("component outside of subckt")
                    elif words[-1] != "0" and words[-2] != "DC":
                        raise CAParsingError("Voltage source is not a shunt!")
                    else:
                        startarray.addshunt(words[1],words[2])
            except CAParsingError as errtype:
                print("Exception during parsing of input file '{0}'".format(filename))
                print("Conflicting line: '{0}'".format(line.strip()))
                print("Exception message:",errtype)
                exit()

def coarseoptimization(startarray, attempts=20, initialtemp=1000, coolingrate=0.95, optimizationcycles = 1000):
    """ Perform initial optimization on the array. 
    Several attempts with different random seeds are started, the best result is returned.

    startarray         = populated input array
    attempts           =  number of different random seeds that are tried
    initialtemp        = starting temperature for the simulated annealing process
    coolingrate        = cooling-rate during simulated annealing
    optimizationcycles = the number of simulated annealing steps (times 100) that are performed for each random seed
    """

    coarseattempts = []

    for i in range(attempts): # 20 coarse attempts
        array=CellArray()
        array.clone(startarray)

        random.seed(i)
        print("\rAttempt: {0}/{1}".format(i+1,attempts),end='')
        sys.stdout.flush()
        temp = initialtemp
        for _ in range (optimizationcycles):
            array.optimizesimulatedannealing(100,temp)
            temp *=coolingrate
        coarseattempts.append(array)
    print()

    ordered = sorted(coarseattempts, key=lambda item: item.totallength)

    print("Candidate lengths:",end='')
    for len in ordered:
        print(" ",len.totallength,end='')
    print("\n")

    array_opt = ordered[0]
    return array_opt

def detailedoptimization(startarray, initialtemp=1, coolingrate=0.95, optimizationcycles = 20000):
    """ Perform detailed optimization on the array. 

    startarray         = populated input array
    initialtemp        = starting temperature for the simulated annealing process
    coolingrate        = cooling-rate during simulated annealing
    optimizationcycles = the number of simulated annealing steps (times 100) that are performed 
    """

    random.seed(1)
    temp = initialtemp
    print()
    for i in range (optimizationcycles):
        array_opt.optimizesimulatedannealing(100,temp)
        temp *=coolingrate
        if (i%(optimizationcycles/20)==0):
            print("\rCompletion: {0:3.1f}%".format(100*i/optimizationcycles),end='')
            sys.stdout.flush()
    print("\rCompletion: {0:3.1f}%\n".format(100))

    return startarray

# ====================================================================
# Configuration area. Will be turned into commandline settings later
# ====================================================================

# !!! You need to update the lines below to adjust for your design!!! 

ArrayXwidth = 24         # This is the width of the grid and should be equal to or larger than the number of I/O pins plus two supply pins!
DesignArea  = 273        # This is the number of unit cells required for the design. It is outputted as "chip area" during the Synthesis step
                        # Fixedio fixes I/O positions within the first row. Leave empty if you want the tool to assign positions.
FixedIO     = []        # Default, tool assigns I/O
# FixedIO     =      ["VCC","inv_a", "inv_y", "xor_a", "xor_b", "xor_y", "and_a", "and_b", "and_y", "d", "clk", "q"] # for moregates.vhd

                        # Insert monitoring LEDs for I/O pins in list
# LEDS        = []      # Default, don't insert any LEDs
LEDS        = ["clk","count.0","count.1","count.2"]         


# Optimizer settings. Only change when needed

AreaMargin = 0.5        # This is additional area that is reserved for empty cells. This value should be larger than zero to allow optimization.
                        # Too large values will result in waste of area.
CoarseAttempts = 2     # 20
CoarseCycles   = 1000   # 1000
FineCycles     = 1000  # 10000 Increase to improve larger designs. 

# Pitch of grid on PCB in mm

PCBPitchx = 2.54*2 # default 5
PCBPitchy = 2.54*3 # default 7

# File names. Don't touch unless you want to modify the flow

InputFileName = "209_synthesized_output.sp"
PCBTemplateFile = "../30_PLACE/board_template.brd" 
PCBOutputFile = "309_board_output.brd"
SpiceOutputFile = "308_extracted_netlist.sp"
FanoutOutputFile = "307_fanout.txt"
NetsOutputFile  = "306_nets.csv"
PlacementOutputFile = "305_placement.csv"

# =========== START OF MAIN ===============================

print("=== Setting up array ===\n")

startarray = CellArray(ArrayXwidth,1+int(math.ceil(DesignArea*(1+AreaMargin)/ArrayXwidth)))

print("Number of cells in design: {0}\nArea margin: {1}%".format(DesignArea,AreaMargin*100))
print("Array Xwidth: {0}\nArray Ywidth: {1}\n".format(startarray.SizeX, startarray.SizeY))

print("=== Parsing input file & Inserting Microcells ===\n")

parsesptocellarray(InputFileName,startarray,FixedIO,LEDS)
print("Parsing successful...")

startarray.rebuildnets()

print("Initial net-length:", startarray.totallength)
print("Initial Placement:\n")

pdframe = startarray.returnpdframe()
pltdata = pdframe.pivot('Y','X','Celltype')
print(pltdata)
print()

print("=== Coarse optimization, picking main candidate ===\n")

start = time.time()
array_opt=coarseoptimization(startarray, attempts=CoarseAttempts, optimizationcycles=CoarseCycles)
array_opt.rebuildnets()  # just to be sure
end = time.time()
print("Elapsed time: {0:6.3f}s\n".format(end-start))

print("=== Detailed optimization ===\n")

print("Initial length:", array_opt.totallength)

start = time.time()
array_opt=detailedoptimization(array_opt, optimizationcycles=FineCycles)
array_opt.rebuildnets()  # just to be sure
end = time.time()

print("Final length:", array_opt.totallength)
print("Elapsed time: {0:6.3f}s".format(end-start))
print()
# array_opt.printarray()

print("=== Final Placement ===\n")

pdframe = array_opt.returnpdframe()
pltdata = pdframe.pivot('Y','X','Celltype')
print(pltdata)
pltdata.to_csv(PlacementOutputFile, sep='\t')

printf("\nMicrocell counts:")
print(pdframe['Celltype'].value_counts())

print("\n=== Final Nets ===\n")

pltdata = pdframe.pivot('Y','X','Nets')
# print(pltdata)
pltdata.to_csv(NetsOutputFile, sep='\t')

with open(FanoutOutputFile, "w") as file:
    for key, net in array_opt.nets.items():
        file.write("{0}\t{1}\n".format(key,len(net[1])))

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

