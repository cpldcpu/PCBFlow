# PCBPlace v0.5a
# 22-Jan-03 cpldcpu
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
class PCBPlacer():
    """ Handles insertion into the actual PCB templates. Load eagle template, insert footprints, output board."""
    def __init__(self, filename):
        self.loadeagle(filename)
        self.components= {}    # Dictionary of components

    def countcomponent(self, componentname, number=1):
        if not componentname in self.components:
            self.components[componentname] = number
        else:
            self.components[componentname] += number

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
        et.SubElement(n_elements, 'element', name = "L"+cellname, library="discrete_logic_components", package="LED0603", value="LED", x=str(x+3.25), y=str(y+3.4) ,rot="R180")
        self.countcomponent("npn transistor")
        self.countcomponent("resistor",2)
        self.countcomponent("led")

        # doppelled
        # et.SubElement(n_elements, 'element', name = "Rl2"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+5.3))
        # et.SubElement(n_elements, 'element', name = "L2"+cellname, library="discrete_logic_components", package="LED0603", value="RES", x=str(x+4.25), y=str(y+3.4) ,rot="R180")
        # self.addcontact("Bc$" + str(self.devcounter) , "Rl2"+cellname, "2" )
        # self.addcontact("Bc$" + str(self.devcounter) , "L2"+cellname, "A" )
        # self.addcontact('VCC' , "Rl2"+cellname, "1" )
        # self.addcontact("B$" + str(self.devcounter+1) , "L2"+cellname, "C")

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

    def insertLTLNOTo(self,x, y, netin, netout, cellname="void"):
        """Insert LTL inverter with open collector at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        self.insertLTLNOTb(x,y,netin, "B$" + str(self.devcounter), netout, cellname, rload=False)
        self.devcounter += 1

    def insertLTLNOTs(self,x, y, netin, netout, cellname="void"):
        """Insert LTL inverter at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        self.insertLTLNOTb(x,y,netin, "B$" + str(self.devcounter), netout, cellname)
        self.devcounter += 1

    def insertLTLNOTb(self,x, y, netin, netbase, netout, cellname="void", rload=True):
        """Insert LTL inverter with base tap at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23", value="PMBT2369", x=str(x+1.55), y=str(y+1.4))
        et.SubElement(n_elements, 'element', name = "L"+cellname, library="discrete_logic_components", package="LED0603", value="LEDW", x=str(x+1.17), y=str(y+3.63) ,rot="R270")
        self.countcomponent("npn transistor")
        self.countcomponent("led")

        if rload:
            et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="discrete_logic_components", package="RES0402", value="RESL", x=str(x+2.94), y=str(y+3.16),rot="R90")
            self.addcontact('VCC' , "Rl"+cellname, "2" )
            self.addcontact(netout , "Rl"+cellname, "1" )
            self.countcomponent("resistor")

        self.addcontact('GND' , "Q"+cellname, "2" )
        self.addcontact(netout , "Q"+cellname, "3")

        self.addcontact(netin, "L"+cellname, "A")
        self.addcontact(netbase, "Q"+cellname, "1")
        self.addcontact(netbase, "L"+cellname, "C")

        self.devcounter += 1

    def insertLTLwand(self, x, y, netins, netout, cellname=""):
        """Insert wired and for LTL logic """

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "R"+cellname, library="discrete_logic_components", package="RES0402", value="RESB", x=str(x+1.17+1.77), y=str(y+6.1-2.92),rot="R90" )
        self.countcomponent("resistor")
        self.addcontact(netout , "R"+cellname, "1" )
        self.addcontact('VCC'  , "R"+cellname, "2" )

        positions = [0 * 1.14, 2 * 1.14, 3 * 1.14, 1 * 1.14,]
        num=0
        for curnet in netins:
            et.SubElement(n_elements, 'element', name = "L"+cellname+str(num), library="discrete_logic_components", package="LED0603", value="LEDR", x=str(x+1.17), y=str(y+3.63-positions[num]) ,rot="R90")
            self.countcomponent("led")
            self.addcontact(netout , "L"+cellname+str(num), "A" )
            self.addcontact(curnet , "L"+cellname+str(num), "C" )
            self.devcounter += 1 
            num = num + 1

    def insertNOT(self,x, y, netin, netout, cellname="void"):
        """Insert RTL inverter at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        self.insertNOTb(x,y,netin, "B$" + str(self.devcounter), netout, cellname, capacitor=True)
        self.devcounter += 1

    def insertNOTb(self,x, y, netin, netbase, netout, cellname="void", capacitor=True):
        """Insert RTL inverter with base tap at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23", value="PMBT2369", x=str(x+1.65), y=str(y+1.25))
        et.SubElement(n_elements, 'element', name = "Rb"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+3.25))
        et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+1), y=str(y+4.3))
        self.countcomponent("npn transistor")
        self.countcomponent("resistor",2)

        self.addcontact('GND' , "Q"+cellname, "2" )
        self.addcontact('VCC' , "Rl"+cellname, "1" )
     
        self.addcontact(netin , "Rl"+cellname, "2" )
        self.addcontact(netin , "Rb"+cellname, "1" )

        self.addcontact(netout , "Q"+cellname, "3")

        self.addcontact(netbase, "Q"+cellname, "1")
        self.addcontact(netbase, "Rb"+cellname, "2")

        if capacitor:
            et.SubElement(n_elements, 'element', name = "C"+cellname, library="discrete_logic_components", package="CAP0402", value="CAP", x=str(x+2.6), y=str(y+3.77),rot="R90")
            self.countcomponent("cap")
            self.addcontact(netin   , "C"+cellname, "2" )
            self.addcontact(netbase , "C"+cellname, "1" )

        self.devcounter += 1

    def insertRTPGTBUFe(self,x, y, netenable, netin, netout, cellname="void"):
        """Insert RTPG transmission gate position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23", value="PMBT2369", x=str(x+1.65), y=str(y+1.25))
        et.SubElement(n_elements, 'element', name = "Rb"+cellname, library="discrete_logic_components", package="RES0402", value="RESB", x=str(x+1), y=str(y+3.25))
        et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="discrete_logic_components", package="RES0402", value="RESB", x=str(x+2.95), y=str(y+2.63),rot="R90" )
        self.countcomponent("npn transistor")
        self.countcomponent("resistor",2)

        self.addcontact(netenable , "Rb"+cellname, "1" )
        self.addcontact("B$" + str(self.devcounter), "Rb"+cellname, "2")

        self.addcontact(netin  , "Q"+cellname, "2" )
        self.addcontact(netout , "Q"+cellname, "3")
        self.addcontact("B$" + str(self.devcounter), "Q"+cellname, "1")

        self.addcontact('VCC'  , "Rl"+cellname, "2" )     
        self.addcontact(netout , "Rl"+cellname, "1" )

        self.devcounter += 1        

    def insertRTPGTBUFc(self,x, y, netenable, netin, netout, cellname="void"):
        """Insert NPN transmission gate at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23", value="PMBT2369", x=str(x+1.65), y=str(y+1.25))
        et.SubElement(n_elements, 'element', name = "Rb"+cellname, library="discrete_logic_components", package="RES0402", value="RESB", x=str(x+1), y=str(y+3.25))
        et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="discrete_logic_components", package="RES0402", value="RESB", x=str(x+2.95), y=str(y+2.63),rot="R90" )
        self.countcomponent("npn transistor")
        self.countcomponent("resistor",2)

        self.addcontact(netenable , "Rb"+cellname, "2" )
        self.addcontact("B$" + str(self.devcounter), "Rb"+cellname, "1")

        self.addcontact(netin , "Q"+cellname, "3" )
        self.addcontact(netout , "Q"+cellname, "2")
        self.addcontact("B$" + str(self.devcounter), "Q"+cellname, "1")

        self.addcontact('VCC'     , "Rl"+cellname, "2" )     
        self.addcontact(netenable , "Rl"+cellname, "1" )

        self.devcounter += 1        

    def insertRTPGNOT(self,x, y, netin, netout, cellname="void",loadresistor=True):
        """Insert RTPG inverter at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        self.insertRTPGNOTb(x,y,netin, "B$" + str(self.devcounter), netout, cellname,loadresistor)

    def insertRTPGNOTb(self,x, y, netin, netbase, netout, cellname="void", loadresistor=True):
        """Insert RTPG inverter with base tap at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23", value="MMBT3904", x=str(x+1.65), y=str(y+1.25))
        et.SubElement(n_elements, 'element', name = "Rb"+cellname, library="discrete_logic_components", package="RES0402", value="RESB", x=str(x+1), y=str(y+3.25))
        self.countcomponent("npn transistor")
        self.countcomponent("resistor")

        self.addcontact(netbase, "Rb"+cellname, "2")
        self.addcontact(netin  , "Rb"+cellname, "1")

        self.addcontact('GND'  , "Q"+cellname, "2")
        self.addcontact(netout , "Q"+cellname, "3")
        self.addcontact(netbase, "Q"+cellname, "1")

        if loadresistor:
            et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="discrete_logic_components", package="RES0402", value="RESL", x=str(x+2.95), y=str(y+2.63),rot="R90" )
            self.countcomponent("resistor")
            self.addcontact('VCC'  , "Rl"+cellname, "2" )     
            self.addcontact(netout , "Rl"+cellname, "1" )

        self.devcounter += 1

    def insertNMOSinv(self,x, y, netin, netdrain, netsource, cellname="void", loadresistor=True):
        """Insert NMOS inverter with base tap at position x,y
        Assumes standard library with transistor and resistor
        supply nets are VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23", value="2N7002", x=str(x+1.65), y=str(y+1.25))
        self.countcomponent("nmos transistor")

        self.addcontact(netsource , "Q" +cellname, "2" )
        self.addcontact(netin     , "Q" +cellname, "1")
        self.addcontact(netdrain  , "Q" +cellname, "3")

        if loadresistor:
            et.SubElement(n_elements, 'element', name = "Rl"+cellname, library="discrete_logic_components", package="RES0402", value="RESL", x=str(x+2.95), y=str(y+2.63),rot="R90" )
            self.countcomponent("resistor")
            self.addcontact('VCC'    , "Rl"+cellname, "2" )
            self.addcontact(netdrain , "Rl"+cellname, "1" )

        self.devcounter += 1

    def insertAMUX(self,x, y, netB1, netB2, netS, netout, cellname="", cap=True):
        """Insert analog multiplexer 74LVC1G3157
        Assumes standard library, supply nets VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SC70-6", value="74LVC1G3157", x=str(x+1.60), y=str(y+1.4+0.6))
        self.countcomponent("amux")

        if cap==True:
            et.SubElement(n_elements, 'element', name = "C"+cellname, library="discrete_logic_components", package="CAP0402", value="CAP", x=str(x+3.6), y=str(y+1.4),rot="R90")
            self.countcomponent("cap")
            self.addcontact('VCC'  , "C"+cellname, "2" )
            self.addcontact('GND'  , "C"+cellname, "1" )

        self.addcontact(netB2  , "Q"+cellname, "1" )
        self.addcontact('GND'  , "Q"+cellname, "2" )
        self.addcontact(netB1  , "Q"+cellname, "3" )
        self.addcontact(netout , "Q"+cellname, "4" )
        self.addcontact('VCC'  , "Q"+cellname, "5" )
        self.addcontact(netS   , "Q"+cellname, "6" )

    def insert1G57(self,x, y, netina, netinb, netinc, netout, cellname="", cap=True):
        """Insert multifunction gate 74LVC1G57
        Assumes standard library, supply nets VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23-6", value="74LVC1G57", x=str(x+1.6), y=str(y+1.4+0.6))
        self.countcomponent("1G57")

        if cap==True:
            et.SubElement(n_elements, 'element', name = "C"+cellname, library="discrete_logic_components", package="CAP0402", value="CAP", x=str(x+4.2), y=str(y+1.4),rot="R90")
            self.countcomponent("cap")
            self.addcontact('VCC'  , "C"+cellname, "2" )
            self.addcontact('GND'  , "C"+cellname, "1" ) 

        self.addcontact(netinb , "Q"+cellname, "1" )
        self.addcontact('GND'  , "Q"+cellname, "2" )
        self.addcontact(netina , "Q"+cellname, "3" )
        self.addcontact(netout , "Q"+cellname, "4" )
        self.addcontact('VCC'  , "Q"+cellname, "5" )
        self.addcontact(netinc , "Q"+cellname, "6" )

    def insert1G175(self,x, y, netclk, netind, netclrn, netoutq, cellname="", cap=True):
        """Insert D-Flipflop 74LVC1G175
        Assumes standard library, supply nets VCC and GND."""

        n_elements = self.n_board.find('elements')
        et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SOT23-6", value="74LVC1G175", x=str(x+1.6), y=str(y+1.4+0.6))
        # et.SubElement(n_elements, 'element', name = "Q"+cellname, library="discrete_logic_components", package="SC70-6", value="74LVC1G175", x=str(x+1.6), y=str(y+1.4+0.6))
        self.countcomponent("1G175")
        cap=False
        if cap==True:
            et.SubElement(n_elements, 'element', name = "C"+cellname, library="discrete_logic_components", package="CAP0402", value="CAP", x=str(x+4.2), y=str(y+1.4),rot="R90")
            self.countcomponent("cap")
            self.addcontact('VCC'  , "C"+cellname, "2" )
            self.addcontact('GND'  , "C"+cellname, "1" )        

        self.addcontact(netclk  , "Q"+cellname, "1" )
        self.addcontact('GND'   , "Q"+cellname, "2" )
        self.addcontact(netind  , "Q"+cellname, "3" )
        self.addcontact(netoutq , "Q"+cellname, "4" )
        self.addcontact('VCC'   , "Q"+cellname, "5" )
        self.addcontact(netclrn , "Q"+cellname, "6" )

    def insertIO(self,x, y, netin, name ="", pullup=False):
        """Insert I/O pin at position x,y"""

        n_elements = self.n_board.find('elements')
        n_iopin = et.SubElement(n_elements, 'element', name = "E"+str(self.devcounter), library="discrete_logic_components", package="1X01", value=name, x=str(x), y=str(y+2.54))
        #  et.SubElement(n_iopin, 'attribute', name= 'VALUE', x=str(x - 1.27), y=str(y), size="1.27", layer="27") # adds name to document layer

        if pullup:
            et.SubElement(n_elements, 'element', name = "Rp"+name, library="discrete_logic_components", package="RES0402", value="RES", x=str(x+2.54), y=str(y+2.54))
            self.addcontact('VCC'   , "Rp"+name, "2" )
            self.addcontact(netin   , "Rp"+name, "1" )

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

@dataclass
class Cell:
    """ Data structure of each cell """
    type:        str
    moveable:    bool
    x:           int
    y:           int
    geometry:    str   # horizontal, center, input
    pin:         list
class CellArray():
    def __init__(self, SizeX=0, SizeY=0):
        self.array = {} # Dictionary of cells
        self.nets = {} # Dictionary of nets
        self.SizeX = SizeX
        self.SizeY = SizeY
        self.rules = [1,1,1]  # 0=weight between rows, 1= weight for local connection, 2=weight for io net
        self.peephole = [] # tag peoplehole optimizations while reading list
        for y in range(SizeY):
            for x in range(SizeX):
                self.array["V"+str(x+SizeX*y)]=Cell('EMPTY',True,x,y,'',[])

    def optimizationrules(self,rules):
        """Updates optimization rules

        Args:
            rules ([arra]): [weight between rows, weight for local connection, weight for io net]
        """
        self.rules=rules
        self.rebuildnets()

    def clone(self, source):
        """ Copy content of another CellArray into this instance"""
        self.array = {} # Dictionary of cells
        self.nets = {} # Dictionary of nets
        self.SizeX = source.SizeX
        self.SizeY = source.SizeY
        self.rules = source.rules
        self.array = deepcopy(source.array)
        self.rebuildnets()

    def outputtoboard(self, board, pitchx = 5, pitchy = 7):
        """ Output content of cellarray to pcb"""
     
        for key, val in self.array.items():
            # celltype = val[0]
            celltype = val.type
            insertcap= val.y%2==0

            ## RTL cells            
            if celltype == 'rt_NOT':
                board.insertNOT(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],key)
            #   elif celltype == '__TBUF_':   # TBUF as synthesized by Yosys - TODO: double check pin assignment!
            #   board.insertTBUF(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)

            # RTPG cells
            elif celltype == 'rtpg_NOT':
                board.insertRTPGNOT(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],key)
            elif celltype == 'rtpg_NOToc':
                board.insertRTPGNOT(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],key, False)
            elif celltype == 'rtpg_TBUFe':    # TBUF as part of latch
                board.insertRTPGTBUFe(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)
            elif celltype == 'rtpg_TBUFc':    # TBUF as part of latch
                board.insertRTPGTBUFc(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)
            elif celltype == 'rtpg_NOTb':
                board.insertRTPGNOTb(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)

            ## Amux logic cells
            elif celltype == 'AMUX':
                board.insertAMUX(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],val.pin[3],key,cap=insertcap)
            ## LVC logic cells
            #   def insert1G175(self,x, y, netclk, netind, netclrn, netoutq, cellname=""):
            #   def insert1G57 (self,x, y, netina, netinb, netinc , netout , cellname=""):
            elif celltype == 'LVC1G175':
                board.insert1G175(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],val.pin[3],key,cap=insertcap)
            elif celltype == 'LVC1G57':                
                board.insert1G57(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],val.pin[3],key,cap=insertcap)
            # nmos cells
            elif celltype == 'NM':                
                board.insertNMOSinv(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)
            elif celltype == 'NMod': 
                board.insertNMOSinv(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key,loadresistor=False)
            # hybrid cells
            # elif celltype == 'NMg':
            #     board.insertNMOSinvg(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)
            ## Generic cells
            elif celltype == 'EMPTY':
                pass            
            elif celltype == 'IO':
                board.insertIO(val.y*pitchx,val.x*pitchy,val.pin[0],str(val.pin[0]))
            elif celltype == 'IOP':
                board.insertIO(val.y*pitchx,val.x*pitchy,val.pin[0],str(val.pin[0]),pullup=True)
            # LED
            elif celltype == 'LED':
                board.insertLED(val.y*pitchx,val.x*pitchy,val.pin[0],key)
            # LTL                
            elif celltype == 'ltl_NOTo':
                board.insertLTLNOTo(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],key)
            elif celltype == 'ltl_NOTs':
                board.insertLTLNOTs(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],key)
            # elif celltype == 'ltl_NOTb':
            #     board.insertLTLNOTb(val.y*pitchx,val.x*pitchy,val.pin[0],val.pin[1],val.pin[2],key)
            elif celltype == 'ltl_WAND1' or celltype == 'ltl_WAND2' or celltype == 'ltl_WAND3' or celltype == 'ltl_WAND4':
                board.insertLTLwand(val.y*pitchx,val.x*pitchy, val.pin[:-1], val.pin[-1], key)
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
                if  (val.type == "IO" or val.type == "IOP") and val.pin[0] != "VCC" and val.pin[0] != "GND":
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

    def printarray(self):
        """ Print array content to stdio"""
        ordered = sorted(self.array.items(), key=lambda item: item[1][2]+self.SizeX*item[1][3])
        columnctr = 0 
        for key, val in ordered:
            #  print("{0}\t".format(val[0]), end="")
            print("{0}\t".format(key), end="")
            columnctr += 1
            if columnctr == self.SizeX:
                print()
                columnctr = 0

    def printnets(self):
        """ list all nets with fanout"""
        for key, net in self.nets.items():
            print("Net: {0:20}Connections: {1}".format(key,len(net[1])))

    def returnpdframe(self):
        """ Return array content as pandas dataframe """
        df=pd.DataFrame.from_dict(self.array, orient='index')
        df.columns =['Celltype','Movable','X','Y','geometry','Nets']
        return df

    def addiocell(self, net,FixedIO=[],LEDS=[],Pullups=[]):
        """ Add I/O cell. I/O Cells are added to row 0 by definition and are fixed."""
        if net in Pullups:
            celltype='IOP'
        else:
            celltype='IO'

        for key, val in self.array.items():
            if val.type == "EMPTY" and val.y == 0:
                if net in FixedIO:
                    if val.x==FixedIO.index(net):
                        del self.array[key]
                        self.array["XIO"+str(val.x)] = Cell(celltype, False, val.x, val.y,'center', [net])
                        if net in LEDS:
                            self.addled(net,val.x,val.y+1)
                        return
                elif val.x>=len(FixedIO):
                    del self.array[key]
                    self.array["XIO"+str(val.x)] = Cell(celltype, False, val.x, val.y,'center', [net])
                    if net in LEDS:
                        self.addled(net,val.x,val.y+1)
                    return  
        raise CAParsingError("Could not insert I/O cell in line zero! Please increase the X-width of the cell array or correct FixedIO assignment.")

    def addled(self, net , x , y ):
        """ add LED at fixed position"""
        for key, val in self.array.items():
            if val.type == "EMPTY" and val.x == x and val.y == y:
                del self.array[key]
                self.array["XLED"+str(val.x)] = Cell('LED', False, val.x, val.y,'input', [net])                
                return
        raise CAParsingError("Could not insert LED cell for NET: "+str(net))
        
    def addlogiccell(self,name,celltype, nets):
        """ Add logic cell. Complex cells are recursively broken down into less complex microcells.
        Special netnames:
          Ending with '!' - local net, cells should be close together
          Ending with '#' - global shared net. To be merged by net optimizer.
        """

        # RTL cells
        if celltype == "rt_NOT":
            self.insertcell(name+"i","rt_NOT", [nets[0], nets[1]])
        elif celltype == "rt_NOR2":
            self.insertcell(name+"a","rt_NOT", [nets[0], nets[2]])
            self.insertcell(name+"b","rt_NOT", [nets[1], nets[2]])
        elif celltype == "rt_NOR3":
            self.insertcell(name+"a","rt_NOT", [nets[0], nets[3]])
            self.insertcell(name+"b","rt_NOT", [nets[1], nets[3]])
            self.insertcell(name+"c","rt_NOT", [nets[2], nets[3]])
        elif celltype == "rt_TBUF_N":
            self.addlogiccell(name+"a","rt_NOR2", [nets[0] , nets[1], name+"a"])
            self.addlogiccell(name+"b","rt_NOT" , [name+"a", nets[2] ])
        elif celltype == "rt_DFF":  # pin order: C, D, Q
            self.insertcell(name+"c#","rt_NOT", [nets[0]  , name+"CI" ])   # clock inversion
            self.insertcell(name+"d" ,"rt_NOT", [name+"CI", name+"CNI"])   # clock inversion
            self.addlogiccell(name+"a","PHLATCH", [name+"CI" , nets[1]  , name+"DI"])  # pin order: E, D, Q
            self.addlogiccell(name+"b","PHLATCH", [name+"CNI", name+"DI", nets[2]  ])  # pin order: E, D, Q
        elif celltype == "PHLATCH":  # pin order: E, D, Q
            self.insertcell(name+"I","rt_NOT", [nets[0], name+"CI"])   # clock inversion (cannot be shared in DFF due to tpd requirements)
            self.addlogiccell(name+"X1","rt_NOR2", [name+"CI" , nets[1]   , name+"X1o"])  # X1: D,CI,X1o
            self.addlogiccell(name+"X2","rt_NOR2", [nets[0]   , nets[2]   , name+"X2o"])  # X2: C,Q,X2o
            self.addlogiccell(name+"X3","rt_NOR2", [name+"X1o", name+"X2o", nets[2]   ])  # X3: X1o,X2o,Q
        elif celltype == "rt_DFF6NOR_NP":  # module rt_DFF6NOR_NP(Cn, D, Q, QN);
            self.addlogiccell(name+"a","rt_NOR2"  , [nets[1]   , name+"b"  , name+"a"  ])   
            self.addlogiccell(name+"b","rt_NOR3"  , [name+"a"  , nets[0]   , name+"c", name+"b" ])               
            self.addlogiccell(name+"c","rt_NOR2"  , [nets[0]   , name+"d"  , name+"c"  ])   
            self.addlogiccell(name+"d","rt_NOR2"  , [name+"c"  , name+"a"  , name+"d"  ])   
            self.addlogiccell(name+"e","rt_NOR2"  , [name+"b"  , nets[2]   , nets[3]   ])   
            self.addlogiccell(name+"f","rt_NOR2"  , [nets[3]   , name+"c"  , nets[2]   ])   
            self.peephole.append(["DFF_with_Qn", nets[2], nets[3] ])
            self.peephole.append(["DFF_with_Qn", nets[3], nets[2] ])
        # Not complete yet
        elif celltype == "rt_DFFNP_CLR":  # pin order: C, nRes, D, Q, Qn
            raise CAParsingError("Macrocell not implemented yet")
        #     self.addlogiccell(name+"a","rt_NOR3"  , [nets[2]   , name+"b"  , nets[1]  , name+"a"   ])   
        #     self.addlogiccell(name+"b","rt_NOR3"  , [name+"a"  , nets[0]   , name+"c" , name+"b" ])               
        #     self.addlogiccell(name+"c","rt_NOR3"  , [nets[0]   , name+"d"  , nets[1]  , name+"c"   ])   
        #     self.addlogiccell(name+"d","rt_NOR2"  , [name+"c"  , name+"a"  , name+"d"  ])   
        #     self.addlogiccell(name+"e","rt_NOR3"  , [name+"b"  , nets[3]   , nets[1]  , nets[4]    ])   
        #     self.addlogiccell(name+"f","rt_NOR2"  , [nets[4]   , name+"c"  , nets[3]   ])   
        #     self.peephole.append(["DFF_with_Qn", nets[3], nets[4] ])
            # e = Qn, f = Q

        # RTPG 
        elif celltype == "rtpg_NOT":
            self.insertcell(name+"i","rtpg_NOT"  , [nets[0], nets[1]])
        elif celltype == "rtpg_NOR2":
            self.insertcell(name+"a","rtpg_NOT"  , [nets[0], nets[2]])
            self.insertcell(name+"b","rtpg_NOToc", [nets[1], nets[2]])
        elif celltype == "rtpg_NOR3":
            self.insertcell(name+"a","rtpg_NOT"  , [nets[0], nets[3]])
            self.insertcell(name+"b","rtpg_NOToc", [nets[1], nets[3]])
            self.insertcell(name+"c","rtpg_NOToc", [nets[2], nets[3]])
        elif celltype == "rtpg_NOR4":
            self.insertcell(name+"a","rtpg_NOT"  , [nets[0], nets[4]])
            self.insertcell(name+"b","rtpg_NOToc", [nets[1], nets[4]])
            self.insertcell(name+"c","rtpg_NOToc", [nets[2], nets[4]])
            self.insertcell(name+"d","rtpg_NOToc", [nets[3], nets[4]])
        elif celltype == "rtpg_XOR2":  
            self.addlogiccell(name+"a","rtpg_TBUFe" , [nets[0]   , nets[1]   , name+"x" ])   
            self.addlogiccell(name+"b","rtpg_TBUFe" , [nets[1]   , nets[0]   , name+"x" ])   
            self.addlogiccell(name+"c","rtpg_NOT"   , [name+"x"  , nets[2]] ) 
        elif celltype == "LATCH3Tn":  # pin order: E, D, Q
            self.addlogiccell(name+"X1","rtpg_TBUFc" , [nets[0]   , nets[1]   , name+"X1o" ])   
            self.addlogiccell(name+"X2","rtpg_NOTb"  , [name+"X3o", name+"X1o", nets[2]    ])
            self.addlogiccell(name+"X3","rtpg_NOT"   , [nets[2]   , name+"X3o"             ])    

        elif celltype == "rtpg_LATCH3Tn":  # pin order: E, D, Q, Qn
            self.addlogiccell(name+"X1","rtpg_TBUFc" , [nets[0]   , nets[1]   , name+"X1o" ])   
            self.addlogiccell(name+"X2","rtpg_NOTb"  , [nets[3]   , name+"X1o", nets[2]    ])
            self.insertcell  (name+"X3","rtpg_NOT"   , [nets[2]   , nets[3]                ])    
        elif celltype == "rtpg_DFF7T_PN":  # pin order: nC, D, Q, Qn
            self.insertcell  (name+"d","rtpg_NOT"     , [nets[0]   , name+"CNI"])   # clock inversion
            self.addlogiccell(name+"a","rtpg_LATCH3Tn", [nets[0]   , nets[1]  , name+"DI", name+"DIN"])  # pin order: E, D, Q, Qn
            self.addlogiccell(name+"b","rtpg_LATCH3Tn", [name+"CNI", name+"DI", nets[2]  , nets[3]   ])  # pin order: E, D, Q, Qn
            self.peephole.append(["DFF_with_Qn", nets[2], nets[3] ])
            self.peephole.append(["DFF_with_Qn", nets[3], nets[2] ])
        elif celltype == "rtpg_DFF7T":  # pin order: nC, D, Q, Qn
            self.insertcell  (name+"d","rtpg_NOT", [nets[0]   , name+"CNI"])   # clock inversion
            self.addlogiccell(name+"a","LATCH3Tn", [nets[0]   , nets[1]  , name+"DI"])  # pin order: E, D, Q, Qn
            self.addlogiccell(name+"b","LATCH3Tn", [name+"CNI", name+"DI", nets[2]  ])  # pin order: E, D, Q, Qn

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
            self.addlogiccell(name+"a","am_LATCH_nClk", [nets[0], nets[1]  , name+"DI"])  # pin order: E, D, Q
            self.addlogiccell(name+"b","am_LATCH"     , [nets[0], name+"DI", nets[2]]  )  # pin order: E, D, Q
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
            self.insertcell(name ,"LVC1G175", [nets[0] , nets[2] , nets[1] , nets[3] ])
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
            self.insertcell(name+"i" ,"NM"    ,   [nets[0] , nets[1]  , "GND"    ])
        elif celltype == "nm_NAND2":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[2]   , name+"x!" ])
            self.insertcell(name+"b" ,"NMod"  ,   [nets[1] , name+"x!" , "GND"     ])
        elif celltype == "nm_NAND3":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[3]   , name+"x!" ])
            self.insertcell(name+"b" ,"NMod"  ,   [nets[1] , name+"x!" , name+"v!" ])
            self.insertcell(name+"c" ,"NMod"  ,   [nets[2] , name+"v!" , "GND"     ])
        elif celltype == "nm_NOR2":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[2]  , "GND"    ])
            self.insertcell(name+"b" ,"NMod"  ,   [nets[1] , nets[2]  , "GND"    ])
        elif celltype == "nm_NOR3":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[3]  , "GND"    ])
            self.insertcell(name+"b" ,"NMod"  ,   [nets[1] , nets[3]  , "GND"    ])
            self.insertcell(name+"c" ,"NMod"  ,   [nets[2] , nets[3]  , "GND"    ])
        elif celltype == "nm_AOI2_2":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[4]   , name+"x!" ])
            self.insertcell(name+"b" ,"NMod"  ,   [nets[1] , name+"x!" , "GND"     ])
            self.insertcell(name+"c" ,"NMod"  ,   [nets[2] , nets[4]   , name+"v!" ])
            self.insertcell(name+"d" ,"NMod"  ,   [nets[3] , name+"v!" , "GND"    ])
        elif celltype == "nm_AOI2_2_2":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[6]   , name+"x!" ])
            self.insertcell(name+"b" ,"NMod"  ,   [nets[1] , name+"x!" , "GND"     ])
            self.insertcell(name+"c" ,"NMod"  ,   [nets[2] , nets[6]   , name+"v!" ])
            self.insertcell(name+"d" ,"NMod"  ,   [nets[3] , name+"v!" , "GND"     ])
            self.insertcell(name+"e" ,"NMod"  ,   [nets[4] , nets[6]   , name+"u!" ])
            self.insertcell(name+"f" ,"NMod"  ,   [nets[5] , name+"u!" , "GND"     ])
        elif celltype == "nm_AOI1_2":
            self.insertcell(name+"a" ,"NM"    ,   [nets[0] , nets[3]  , "GND"     ])
            self.insertcell(name+"b" ,"NMod"  ,   [nets[1] , nets[3]  , name+"x!" ])
            self.insertcell(name+"c" ,"NMod"  ,   [nets[2] , name+"x!" , "GND"    ])
        #elif celltype == "nm_DFF":  # pin order: C, D, Q
        #    self.addlogiccell(name+"c","nm_NOT"    , [nets[0], name+"CI"])   # clock inversion
        #    self.addlogiccell(name+"a","nm_PHLATCH", [name+"CI", nets[1], name+"DI"])  # pin order: E, D, Q
        #    self.addlogiccell(name+"b","nm_PHLATCH", [nets[0], name+"DI", nets[2]])  # pin order: E, D, Q
            # self.addlogiccell(name+"a","nm_5TLATCH", [name+"CI", nets[1], name+"DI"])  # pin order: E, D, Q
            # self.addlogiccell(name+"b","nm_5TLATCH", [nets[0], name+"DI", nets[2]])  # pin order: E, D, Q
        elif celltype == "nm_PHLATCH":  # pin order: E, D, Q
            self.addlogiccell(name+"I" ,"nm_NOT" , [nets[0]   , name+"CI"])   # clock inversion (cannot be shared in DFF due to tpd requirements)
            self.addlogiccell(name+"X1","nm_NOR2", [name+"CI" , nets[1]   , name+"X1o"])  # X1: D,CI,X1o
            self.addlogiccell(name+"X2","nm_NOR2", [nets[0]   , nets[2]   , name+"X2o"])  # X2: C,Q,X2o
            self.addlogiccell(name+"X3","nm_NOR2", [name+"X1o", name+"X2o", nets[2]   ])  # X3: X1o,X2o,Q
        elif celltype == "nm_DFFNP":  # pin order: C, D, Q, Qn
            self.addlogiccell(name+"a","nm_NAND2"  , [nets[1]   , name+"b"  , name+"a"  ])   
            self.addlogiccell(name+"b","nm_NAND3"  , [name+"a"  , nets[0]   , name+"c", name+"b" ])               
            self.addlogiccell(name+"c","nm_NAND2"  , [nets[0]   , name+"d"  , name+"c"  ])   
            self.addlogiccell(name+"d","nm_NAND2"  , [name+"c"  , name+"a"  , name+"d"  ])   
            self.addlogiccell(name+"e","nm_NAND2"  , [name+"b"  , nets[2]   , nets[3]   ])   
            self.addlogiccell(name+"f","nm_NAND2"  , [nets[3]   , name+"c"  , nets[2]   ])   

            self.peephole.append(["DFF_with_Qn", nets[2], nets[3] ])
            self.peephole.append(["DFF_with_Qn", nets[3], nets[2] ])
            # e = Qn, f = Q
        elif celltype == "nm_DFFNP_CLR":  # pin order: C, nRes, D, Q, Qn
            self.addlogiccell(name+"a","nm_NAND3"  , [nets[2]   , name+"b"  , nets[1]  , name+"a"   ])   
            self.addlogiccell(name+"b","nm_NAND3"  , [name+"a"  , nets[0]   , name+"c" , name+"b" ])               
            self.addlogiccell(name+"c","nm_NAND3"  , [nets[0]   , name+"d"  , nets[1]  , name+"c"   ])   
            self.addlogiccell(name+"d","nm_NAND2"  , [name+"c"  , name+"a"  , name+"d"  ])   
            self.addlogiccell(name+"e","nm_NAND3"  , [name+"b"  , nets[3]   , nets[1]  , nets[4]    ])   
            self.addlogiccell(name+"f","nm_NAND2"  , [nets[4]   , name+"c"  , nets[3]   ])   
            self.peephole.append(["DFF_with_Qn", nets[3], nets[4] ])
            self.peephole.append(["DFF_with_Qn", nets[4], nets[3] ])
            # e = Qn, f = Q

        # LTL
        elif celltype == "ltl_NOT":  
            self.insertcell(name+"a" ,"ltl_WAND1"   ,   [nets[0]  , name+"i!" ])
            self.insertcell(name+"b" ,"ltl_NOTs"    ,   [name+"i!", nets[1]   ])
        elif celltype == "ltl_NAND2":  
            self.insertcell(name+"a" ,"ltl_WAND2"   ,   [nets[0]  , nets[1]   , name+"i!" ])
            self.insertcell(name+"b" ,"ltl_NOTs"    ,   [name+"i!", nets[2]   ])
        elif celltype == "ltl_NAND3":
            self.insertcell(name+"a" ,"ltl_WAND3"   ,   [nets[0]  , nets[1]   , nets[2]  , name+"i!" ])
            self.insertcell(name+"b" ,"ltl_NOTs"    ,   [name+"i!", nets[3]   ])
        elif celltype == "ltl_NAND4":
            self.insertcell(name+"a" ,"ltl_WAND4"   ,   [nets[0]  , nets[1]   , nets[2]  , nets[3]  , name+"i!" ])
            self.insertcell(name+"b" ,"ltl_NOTs"    ,   [name+"i!", nets[4]   ])
        elif celltype == "ltl_DFFNP":  # pin order: C, D, Q, Qn
#            self.addlogiccell(name+"a","ltl_NAND2"  , [nets[1]   , name+"b"  , name+"a"  ])     # pure LTL version fail simulation, but works in circuit
            self.addlogiccell(name+"a","nm_NAND2"  , [nets[1]   , name+"b"  , name+"a"  ])   
            self.addlogiccell(name+"b","ltl_NAND3"  , [name+"a"  , nets[0]   , name+"c", name+"b" ])               
            self.addlogiccell(name+"c","ltl_NAND2"  , [nets[0]   , name+"d"  , name+"c"  ])   
            self.addlogiccell(name+"d","ltl_NAND2"  , [name+"c"  , name+"a"  , name+"d"  ])   
            self.addlogiccell(name+"e","ltl_NAND2"  , [name+"b"  , nets[2]   , nets[3]   ])   
            self.addlogiccell(name+"f","ltl_NAND2"  , [nets[3]   , name+"c"  , nets[2]   ])   
            # self.peephole.append(["DFF_with_Qn", nets[2], nets[3] ])
            # self.peephole.append(["DFF_with_Qn", nets[3], nets[2] ])
            # e = Qn, f = Q
        elif celltype == "ltl_DFFNP_CLR":  # pin order: C, nRes, D, Q, Qn
            self.addlogiccell(name+"a","ltl_NAND3"  , [nets[2]   , name+"b"  , nets[1]  , name+"a"   ])   
            self.addlogiccell(name+"b","ltl_NAND3"  , [name+"a"  , nets[0]   , name+"c" , name+"b" ])               
            self.addlogiccell(name+"c","ltl_NAND3"  , [nets[0]   , name+"d"  , nets[1]  , name+"c"   ])   
            self.addlogiccell(name+"d","ltl_NAND2"  , [name+"c"  , name+"a"  , name+"d"  ])   
            self.addlogiccell(name+"e","ltl_NAND3"  , [name+"b"  , nets[3]   , nets[1]  , nets[4]    ])   
            self.addlogiccell(name+"f","ltl_NAND2"  , [nets[4]   , name+"c"  , nets[3]   ])   
            self.peephole.append(["DFF_with_Qn", nets[3], nets[4] ])
            self.peephole.append(["DFF_with_Qn", nets[4], nets[3] ])
            # e = Qn, f = Q
        else:
            self.insertcell(name,celltype, nets)

    def insertcell(self,name,celltype, nets, geometry='horizontal'):
        for key, val in self.array.items():
            if val.type == celltype and val.pin == nets:
                print ("Skipping functionally redundant Microcell: {0} {1} ".format(celltype, nets))
                return                    

        for key, val in self.array.items():
            if val.type == "EMPTY" and val.y > 0:
                #  print(name,nets)
                del self.array[key]
                self.array[name] = Cell(celltype, True, val.x, val.y, geometry, nets)
                return
        raise CAParsingError("Failure to insert Cell. Cell array size too small for design! Increase number of cells.")

    def addshunt(self,net1,net2):
        """ Add shunt between two nets. One netname will be eliminated in the process. Attention: Currently this
            does not work with multiple internal shunts. Please flatten your design before starting placement!"""
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
         # TODO: #1 Introduce handling of shunting more than one I/O pin to internal net

        self.replacenet(replacenet, replacewith)

    def rebuildnets(self):
        """ Rebuild list of nets from cellarray."""
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

    def updatenetlength(self,netname):
        """ Update the length of a specific net."""
        if not netname in self.nets:
            print("Net not found!")
            return
        cells = self.nets[netname][1]

        # Use half perimeter wirelength algorithm (HPWL)
        xmin, xmax = self.SizeX+1, -1               
        ymin, ymax = self.SizeY+1, -1                

        isionet = False
        for currentcell in cells:
            xpos=self.array[currentcell].x
            ypos=self.array[currentcell].y

            # Optimize for pin positions
            if self.array[currentcell].geometry == "horizontal":  # cell with horizontal input/output
                if self.array[currentcell].type[0:2] == "NM": # Net order is G D S,  Right: D, Left G,S
                    ypos = ypos + 0.5 * (1 if self.array[currentcell].pin[1] == netname else -1)
                elif self.array[currentcell].pin[-1] == netname: 
                    ypos = ypos + 0.5 # net is on output (right side of cell)
                else:
                    ypos = ypos - 0.5 # net is on input (left side of cell)
            elif self.array[currentcell].geometry == "input":   # cell with input on left side
                ypos = ypos - 0.5 # net is on input (left side of cell)
            elif self.array[currentcell].geometry == "center":   # cell with central connection
                pass

            xmin = xmin if xpos>xmin else xpos
            xmax = xmax if xpos<xmax else xpos
            ymin = ymin if ypos>ymin else ypos
            ymax = ymax if ypos<ymax else ypos

            if self.array[currentcell].type == "IO" or self.array[currentcell].type == "IOP":
                isionet = True

        HPWL = self.rules[0]*(xmax-xmin)+ymax-ymin # priorize horizontal connections

        if netname[-1] == '!':     # local connection identified
            HPWL = HPWL * self.rules[1]        # priorize internal connections

        if isionet == True:
            HPWL = HPWL * self.rules[2]        # priorize I/O

        self.nets[netname][0] = HPWL

    def swapcells(self, cell1, cell2):
        """ Swap two cells and update the net lengths selectiviely."""
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
    
    def removecell(self, cellkey):
        """Removes a cell from the grid and replaces it with an empty one

        Args:
            cellkey (str): cell key            
        """
        val = self.array[cellkey]
        del self.array[cellkey]
        self.array[cellkey] = Cell('EMPTY', True, val.x, val.y, "None", [])

    def replacenet(self, replacenet, replacewith):
        """Replace one net with another

        Args:
            replacenet ([type]): [description]
            replacewith ([type]): [description]
        """

        for key, val in self.array.items():    
            if val.type == 'EMPTY':
                 continue
            self.array[key].pin = [replacewith if net==replacenet else net for net in val.pin]

        for idx, item in enumerate(self.peephole):
            if item[0] == "DFF_with_Qn":
                self.peephole[idx] = [replacewith if net==replacenet else net for net in item]

    def peepholeoptimizer(self):
        """Execute on collected peephole optimizations 
        """
        for item in self.peephole:
            if item[0] =="DFF_with_Qn":  # Eliminate inverters by replacing their output net with Qn. item[1] is Q item [2] is Qn              
                tryltl = [key for key,val in self.array.items() if val.type == "ltl_WAND1" and val.pin[0] == item[1]]
                if tryltl != []:
                    cellkey1=tryltl[0]
                    midnet = self.array[cellkey1].pin[1]
                    cellkey2 = [key for key,val in self.array.items() if val.type == "ltl_NOTs" and val.pin[0] == midnet][0]
                    endnet = self.array[cellkey2].pin[1]
                    
                    self.removecell(cellkey1)
                    self.removecell(cellkey2)

                    self.replacenet(endnet, item[2])

                    print(f"Removed cells {cellkey1},{cellkey2}, integrated net: {endnet} into {item[2]}")
                    continue
                # RTL, nmos, RTPG
                for cellkey in [key for key,val in self.array.items() if ( val.type == "rt_NOT" or val.type == "rtpg_NOT" or val.type == "NM") and val.pin[0] == item[1]]:
                    if cellkey[-1:] == 'i':
                        endnet = self.array[cellkey].pin[1] 
                    
                        self.removecell(cellkey)
                        self.replacenet(endnet, item[2])

                        print(f"Removed cell {cellkey}, integrated net: {endnet} into {item[2]}")
                continue
            print(f"Warning: Unknown Peephole optimizhation {item}")        

    def optimizerandomexchange(self, iterations = 1000):
        """ Optimize by random cell swapping."""
        for i in range(iterations):
            cell1, cell2 = random.sample(self.array.keys(),2)
            if self.array[cell1][1] == False or self.array[cell2][1] == False:
                # Don't exchange fixed cells
                continue
            oldnetlength = self.totallength
            self.swapcells(cell1,cell2)
            if self.totallength > oldnetlength:
                self.swapcells(cell1,cell2)

    def optimizesimulatedannealing(self, iterations = 1000, temperature = 1):
        """ Optimize by simulated annealing. """
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

def parsesptocellarray(filename, startarray:CellArray,FixedIO=[],LEDS=[],Pullups=[]):
    """ Parse a spice netlist given as file to a CellArray structure    
    filename = name of spice netlist
    inputarray = CellArray 
    """
    subckt = ""
    with open(filename, "r") as file:
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
                        startarray.addiocell(net, FixedIO,LEDS,Pullups)
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
    for length in ordered:
        print(" ",length.totallength,end='')
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

ArrayXwidth = 28        # This is the width of the grid and should be equal to or larger than the number of I/O pins plus two supply pins!
DesignArea  = 720        # This is the number of unit cells required for the design. It is outputted as "chip area" during the Synthesis step
                        # Fixedio fixes I/O positions within the first row. Leave empty if you want the tool to assign positions.
FixedIO     = []        # Default, tool assigns I/O
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
pltdata = pdframe.pivot('Y','X','Celltype')
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
pltdata = pdframe.pivot('Y','X','Celltype')
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

print("=== Final Placement ===\n")

pdframe = array_opt.returnpdframe()
pltdata = pdframe.pivot('Y','X','Celltype')
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

