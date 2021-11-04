library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity gatesx is
	port (a,b:	in	std_logic;
	      c,d:	in	std_logic;
		  x,y,cout: out std_logic
	);
end;

architecture main of gatesx is
    signal adder: unsigned(1 downto 0);
begin
    x <= a AND b;
    
    adder <= ("0" & c) + ("0" & d);
    y <= adder(0);
    cout <= adder(1);
end;
