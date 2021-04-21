import math

import numpy


class BufferAzimuth:
    def __init__(self, bufSize, targetAz, accuracy):
        self.windowSize = bufSize
        self.az_list = []
        self.accuracy = accuracy
        self.targetAzimuth = targetAz
        self.test = []

    def addElem(self, azimuth):
        if len(self.az_list) >= self.windowSize * 2 + 1:
            self.az_list.pop(0)
            self.test.pop(0)
        self.az_list.append(azimuth)
        self.test.append(int(math.fabs(self.targetAzimuth - azimuth) <= self.accuracy or
                         math.fabs(self.targetAzimuth + 180 - azimuth) <= self.accuracy))

    def getAverage(self):
        if sum(self.test) > self.windowSize:
            return self.targetAzimuth
        else:
            return self.targetAzimuth + 90
        # return numpy.average(self.az_list)

#
# f = fifoGetBuf(2)
# f.addElem(0)
# f.addElem(1)
# f.addElem(2)
# f.addElem(3)
# f.addElem(4)
# print(f.az_list)
# f.addElem(5)
# print(f.az_list)