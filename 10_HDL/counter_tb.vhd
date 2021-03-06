library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity testbench is
end;

architecture testmain of testbench is

  component counterx is
    port (clk:	in	std_logic;
        nrst:	in	std_logic;
        count: out std_logic_vector(2 downto 0)
    );
  end component;

  signal clk,nrst:  std_logic;
  signal count:    std_logic_vector(2 downto 0);

begin 

ctr:  counterx  port map(clk => clk, nrst => nrst, count => count);

  process    
  begin
    nrst <= '0';
    clk <= '0';
    WAIT FOR 50 ns;
    clk <= '1';
    WAIT FOR 50 ns;
    nrst <= '1';

    loop
      clk <= '0';
      WAIT FOR 50 ns;
      clk <= '1';
      WAIT FOR 50 ns;		-- clock.		
    end loop ; -- identifier

	  assert false report "END of testbench reached";

    end process;
end;





