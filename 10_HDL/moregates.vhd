library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity gatesx is
	port (inv_a:	in	std_logic;
          inv_y:    out std_logic;

          xor_a:	in	std_logic;
          xor_b:	in	std_logic;
          xor_y:    out std_logic;

          and_a:	in	std_logic;
          and_b:	in	std_logic;
          and_y:    out std_logic;

	      d,clk:	in	std_logic;
		  q:        out std_logic
	);
end;

architecture main of gatesx is
    signal reg: std_logic;   
begin
    process (clk)
    begin
        if rising_edge(clk) then
            reg <= d;
        end if;
    end process;

    q <= reg;

    and_y <= and_a AND and_b;
    xor_y <= xor_a XOR xor_b;
    inv_y <= NOT inv_a;
end;
