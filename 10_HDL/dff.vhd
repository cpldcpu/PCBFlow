library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity counterx is
	port (clk:	in	std_logic;
	      rst:	in	std_logic;
		  count: out std_logic_vector(2 downto 0)
	);
end;

architecture main of counterx is
	signal  cnt:	std_logic;
begin

 	process (clk,rst)
	begin
		if rising_edge(clk) then
			if (rst = '1') then
				cnt <= '0';
			else
				cnt <= NOT cnt;
			end if;			
		end if;
	end process;

	count <= cnt & cnt & cnt;
end;
