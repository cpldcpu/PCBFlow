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
	signal  cnt:	unsigned(2 downto 0);
begin

 	process (clk,rst)
	begin
        if rst = '0' then
            cnt <= (others => '0');
		elsif rising_edge(clk) then
            cnt <= cnt + 1;
		end if;
	end process;

	count <= std_logic_vector(cnt);		
end;
