# -*- coding: utf-8 -*-

class AzimuthHistogram:
    def __init__(self, size):
        self.shift = True
        self.step = int(360 / int(360 // size)) # шаг построения - ширина сектора, в градусах
        self.sectors = [0 for x in range(0,359,self.step)] # количество точек данных в каждом секторе

    def getSector(self, a):
        if self.shift:
            return int((a-1) % 360 // self.step)
        else:
            return int((a + self.step / 2) % 360 // self.step)

    def add(self, a):
        self.sectors[self.getSector(a)] += 1
        self.sectors[self.getSector(a+180)] += 1

    def getMostFrequent(self):
        max = 0
        max_idx = -1
        for n in range(0, len(self.sectors)):
            if self.sectors[n] > max:
                max = self.sectors[n]
                max_idx = n
        if max_idx >= 0:
            return max_idx * self.step
        else:
            return None

