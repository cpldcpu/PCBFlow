library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;




entity dice555johnson is
	port (clk:		in	std_logic;
	      n_clk:	in	std_logic;
		  nreset:	in std_logic;
		  dice: out std_logic_vector(3 downto 0)
	);
end;

architecture main of dice555johnson is
    signal  cnt:	unsigned(2 downto 0);
begin
 	process (clk,n_clk,nreset)
	begin
		if nreset = '0' then
			cnt <= "000";
		elsif rising_edge(clk) then
            cnt <= cnt(1 downto 0) & NOT cnt(2);
		end if;
	end process;

--  1     2     
--  3  0  3
--  2     1

-- Encoding:
-- 001  1
-- 010  2
-- 011  1,2
-- 100  2,3
-- 101  1,2,3
-- 110  2,3,4

-- drive inverted LEDs
dice(0) <= NOT cnt(0);
dice(1) <= '1' when (cnt = "011") else '0';
dice(2) <= NOT cnt(2);
dice(3) <= '0' when (cnt = "10X") else '1';

end;
