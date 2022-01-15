library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;




entity dice555johnson is
	port (clk:		in	std_logic;
	    --   n_clk:	in	std_logic;
		  nrst:	in std_logic;
		  dice: out std_logic_vector(3 downto 0)
	);
end;

architecture main of dice555johnson is
    signal  cnt:	unsigned(2 downto 0);
begin
 	process (clk,nrst)
	begin
		-- sync reset implementation to allow using yosys internal digital simulation
		-- if rising_edge(clk) then 
		-- 	if nrst = '0' then
		-- 		cnt <= "000";
		-- 	else
        --     	cnt <= cnt(1 downto 0) & NOT cnt(2);
		-- 	end if;
		-- end if;

		-- async reset for synthesis		
		if nrst = '0' then
			cnt <= "000";
		elsif rising_edge(clk) then 
			cnt <= cnt(1 downto 0) & NOT cnt(2);
		end if;
	end process;

--  1     2     
--  3  0  3
--  2     1

-- Encoding:
-- 011  0
-- 000  1
-- 001  0,1
-- 110  1,2
-- 111  0,1,2
-- 100  1,2,3

-- 101  invalid
-- 010  invalid

-- drive inverted LEDs
dice(0) <= NOT cnt(0);
dice(1) <= '1' when (cnt = "011") else '0';
dice(2) <= NOT cnt(2);
dice(3) <= '0' when (cnt(2 downto 1) = "10") else '1';

end;
