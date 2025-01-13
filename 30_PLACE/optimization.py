import random
import sys
import time
import math
import numpy as np
from .CellArray import CellArray

def coarseoptimization(startarray:CellArray, attempts:int=20, initialtemp:float=1000, coolingrate:float=0.95, optimizationcycles:int = 1000) -> CellArray:
    """ Perform initial optimization on the array. 
    Several attempts with different random seeds are started, the best result is returned.

    startarray         = populated input array
    attempts           =  number of different random seeds that are tried
    initialtemp        = starting temperature for the simulated annealing process
    coolingrate        = cooling-rate during simulated annealing
    optimizationcycles = the number of simulated annealing steps (times 100) that are performed for each random seed
    """

    coarseattempts = []

    for i in range(attempts): # 20 coarse attempts
        array=CellArray()
        array.clone(startarray)

        random.seed(i)
        print("\rAttempt: {0}/{1}".format(i+1,attempts),end='')
        sys.stdout.flush()
        temp = initialtemp
        for _ in range (optimizationcycles):
            array.optimizesimulatedannealing(100,temp)
            temp *=coolingrate
        coarseattempts.append(array)
    print()

    ordered = sorted(coarseattempts, key=lambda item: item.totallength)

    print("Candidate lengths:",end='')
    for length in ordered:
        print(" ",length.totallength,end='')
    print("\n")

    array_opt = ordered[0]
    return array_opt

def detailedoptimization(startarray, initialtemp=1, coolingrate=0.95, optimizationcycles = 20000):
    """ Perform detailed optimization on the array. 

    startarray         = populated input array
    initialtemp        = starting temperature for the simulated annealing process
    coolingrate        = cooling-rate during simulated annealing
    optimizationcycles = the number of simulated annealing steps (times 100) that are performed 
    """

    random.seed(1)
    temp = initialtemp
    print()
    for i in range (optimizationcycles):
        array_opt.optimizesimulatedannealing(100,temp)
        temp *=coolingrate
        if (i%(optimizationcycles/20)==0):
            print("\rCompletion: {0:3.1f}%".format(100*i/optimizationcycles),end='')
            sys.stdout.flush()
    print("\rCompletion: {0:3.1f}%\n".format(100))

    return startarray
