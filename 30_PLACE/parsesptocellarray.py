from .CellArray import CellArray, CAParsingError

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
