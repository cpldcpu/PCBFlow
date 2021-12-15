library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


--  2     3     
--  4  1  4
--  3     2

-- Encoding:
-- 001  1
-- 010  2
-- 011  1,2
-- 100  2,3
-- 101  1,2,3
-- 110  2,3,4

entity dice555 is
	port (clk:	in	std_logic;
	      rst:	in	std_logic;
		  dice: out std_logic_vector(3 downto 0)

	);
end;

architecture main of dice555 is
    signal  cnt:	unsigned(2 downto 0);
begin
 	process (clk,rst)
	begin
		if rising_edge(clk) then
			if (rst = '0') then
                cnt <= "001";
            else 
                if cnt < 6 then
                    cnt <= cnt + 1;
                else
                    cnt <= "001";
                end if;
			end if;			
		end if;
	end process;

dice(0) <= cnt(0);
dice(1) <= '0' when (cnt = "001") else '1';
dice(2) <= cnt(2);
dice(3) <= '1' when (cnt = "11X") else '0';
 
end;
