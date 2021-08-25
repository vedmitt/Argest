import numpy as np


class NDArrayManager:

    def __init__(self):
        pass

    def getHeadAndBodyFromNDArray(self, ndarr):
        return ndarr[0], ndarr[1:]

    def getVectorOfData(self, data, ind):
        return [row[ind] for row in data]

    def appendToNDArray(self, arr, val, axis):
        return np.append(arr, val, axis=axis)

    def appendColumnsWithHeader(self, mkeys, mdata, new_keys, new_data):
        nd = NDArrayManager()

        for f in new_keys:
            mkeys = nd.appendToNDArray(mkeys, [f], 0)
        # print(mkeys)

        for v in new_data:
            n = [[str(t)] for t in v]
            mdata = nd.appendToNDArray(mdata, n, 1)
        # print(mdata)

        return mkeys, mdata
