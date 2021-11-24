echo "Cleaning HDL files"
cd 10_HDL/
make clean
cd ..

echo "Cleaning work directory"
cd Work/
rm -f *.cf *.dot *.pdf *.txt *.sp *.o *.json *.csv *.brd *.pro *.b*
cd ..