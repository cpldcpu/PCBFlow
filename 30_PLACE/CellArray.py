from copy import deepcopy
from dataclasses import dataclass
import random
import sys
import math
import numpy as np
import pandas as pd

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

        if any(net == x[0] for x in FixedIO):   # check if net is in FixedIO list and skip insertion if so
            return
        
        for key, val in self.array.items():
            if val.type == "EMPTY" and val.y == 0:
                del self.array[key]
                self.array["XIO"+str(val.x)] = Cell(celltype, False, val.x, val.y,'center', [net])
                if net in LEDS:
                    self.addled(net,val.x,val.y+1)
                return  

        # for key, val in self.array.items():
        #     if val.type == "EMPTY" and val.y == 0:
        #         if net in FixedIO:
        #             if val.x==FixedIO.index(net):
        #                 del self.array[key]
        #                 self.array["XIO"+str(val.x)] = Cell(celltype, False, val.x, val.y,'center', [net])
        #                 if net in LEDS:
        #                     self.addled(net,val.x,val.y+1)
        #                 return
        #         elif val.x>=len(FixedIO):
        #             del self.array[key]
        #             self.array["XIO"+str(val.x)] = Cell(celltype, False, val.x, val.y,'center', [net])
        #             if net in LEDS:
        #                 self.addled(net,val.x,val.y+1)
        #             return  
        raise CAParsingError("Could not insert I/O cell in line zero! Please increase the X-width of the cell array or correct FixedIO assignment.")

    def addfixediocells(self,  FixedIO=[]):
        """ add all FixedIO locations"""
        for net, iox, ioy in FixedIO:
            if net in Pullups:
                celltype='IOP'
            else:
                celltype='IO'

            for key, val in self.array.items():
                if val.type == "EMPTY" and val.x == iox and val.y == ioy:
                    del self.array[key]
                    self.array["XIO"+str(net)] = Cell(celltype, False, val.x, val.y,'input', [net])                
                    break
            else:
                raise CAParsingError("Could not insert IO cell for NET: "+str(net))

    def addled(self, net , x , y ):
        """ add LED at fixed position"""
        for key, val in self.array.items():
            if val.type == "EMPTY" and val.x == x and val.y == y:
                del self.array[key]
                self.array["XLED"+str(val.x)] = Cell('LED', False, val.x, val.y,'input', [net])                
                return
        raise CAParsingError("Could not insert LED cell for NET: "+str(net))
        
    def addlogiccell(self,name:str,celltype:str, nets:list) -> None:
        """ Add logic cell. Complex cells are recursively broken down into less complex microcells.
        Special netnames:
          Ending with '!' - local net, cells should be close together
          Ending with '#' - global shared net. To be merged by net optimizer.
          Ending with 'B' - Buffered and duplicated net
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
            self.addlogiccell(name+"a","ltl_NAND2"  , [nets[1]   , name+"b"  , name+"a"  ])     # pure LTL version fail simulation, but works in circuit
            # self.addlogiccell(name+"a","nm_NAND2"  , [nets[1]   , name+"b"  , name+"a"  ])   
            self.addlogiccell(name+"b","ltl_NAND3"  , [name+"a"  , nets[0]   , name+"c", name+"b" ])               
            self.addlogiccell(name+"c","ltl_NAND2"  , [nets[0]   , name+"d"  , name+"c"  ])   
            self.addlogiccell(name+"d","ltl_NAND2"  , [name+"c"  , name+"a"  , name+"d"  ])   
            self.addlogiccell(name+"e","ltl_NAND2"  , [name+"b"  , nets[2]   , nets[3]   ])   
            self.addlogiccell(name+"f","ltl_NAND2"  , [nets[3]   , name+"c"  , nets[2]   ])   
            self.peephole.append(["DFF_with_Qn", nets[2], nets[3] ])
            self.peephole.append(["DFF_with_Qn", nets[3], nets[2] ])
            # e = Qn, f = Q
        elif celltype == "ltl_DFFNP_CLR":  # pin order: C, nRes, D, Q, Qn
            self.addlogiccell(name+"a","ltl_NAND3"  , [nets[2]   , name+"b"  , nets[1]  , name+"a"   ])   
            self.addlogiccell(name+"b","ltl_NAND3"  , [name+"a"  , nets[0]   , name+"c" , name+"b" ])               
            self.addlogiccell(name+"c","ltl_NAND3"  , [nets[0]   , name+"d"  , nets[1]  , name+"c"   ])   
            self.addlogiccell(name+"d","ltl_NAND2"  , [name+"c"  , name+"a"
