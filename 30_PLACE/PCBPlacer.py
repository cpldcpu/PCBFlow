from lxml import etree as et

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
