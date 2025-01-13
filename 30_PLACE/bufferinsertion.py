from .CellArray import CellArray

def bufferinsertion(array_in: CellArray, netkey: str, maxfo: int = 8) -> bool:
    """ insert buffers into net designated with "netkey".

    Args:
        array_opt (CellArray): array
        netkey (str): net for buffer insertion
        maxfo (int, optional): _description_. Defaults to 8.

    Returns:
        bool: True if 
    """

    data = array_in.nets[netkey]

    cells = data[1]
    generatorcells = [cellkey for cellkey in cells if array_in.array[cellkey].pin[-1] == netkey]
    consumercells = [cellkey for cellkey in cells if array_in.array[cellkey].pin[-1] != netkey]

    numclusters = int(len(consumercells) / maxfo + 1)

    print(f">Net:{netkey} Length:{len(consumercells)} Drivercells:{generatorcells} ", end='')

    if len(generatorcells) == 1 and generatorcells[0][-1] == "i":
        subclusters = np.array_split(consumercells, numclusters)
        bestsumsquares = 1e10

        for i in range(10000):
            idc1, idc2 = random.sample(range(len(subclusters)), 2)
            idx1 = random.sample(range(len(subclusters[idc1])), 1)
            idx2 = random.sample(range(len(subclusters[idc2])), 1)

            subclusters[idc1][idx1], subclusters[idc2][idx2] = subclusters[idc2][idx2], subclusters[idc1][idx1]

            sumsquares = 0
            for cluster in subclusters:
                meanx = np.mean([array_opt.array[key].x for key in cluster])
                meany = np.mean([array_opt.array[key].y for key in cluster])
                sumsquares += np.sum([(array_opt.array[key].x - meanx) ** 2 for key in cluster]) + np.sum(
                    [(array_opt.array[key].y - meany) ** 2 for key in cluster])

            delta = sumsquares - bestsumsquares

            if delta < 0:
                bestsumsquares = sumsquares
            else:
                subclusters[idc1][idx1], subclusters[idc2][idx2] = subclusters[idc2][idx2], subclusters[idc1][idx1]

        numdix = 0
        sourcenet = array_in.array[generatorcells[0]].pin[0]
        celltype = array_in.array[generatorcells[0]].type
        numcluster = len(subclusters)
        print(f">Sourcenet: {sourcenet} Inserting {numcluster} subnets")
        for cluster in subclusters:
            replacenet = netkey
            replacewith = netkey + "B" + str(numdix)
            array_in.addlogiccell(generatorcells[0] + "B" + str(numdix), celltype, [sourcenet, replacewith])
            numdix += 1
            for curcell in cluster:
                array_in.array[curcell].pin = [replacewith if net == replacenet else net for net in
                                               array_in.array[curcell].pin]

        array_in.removecell(generatorcells[0])
        return True
    print(">Net not driven by inverter")
    return False
