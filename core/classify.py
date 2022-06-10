# -*- coding: utf-8 -*-

from ..core.spatial import BBox, rotate, dist, angle180

import numpy as np
import math, bisect

class PointCache:  # кэш для координат точек и необходимой статистики
    def __init__(self, capacity: int = 100):
        self.capacity = capacity  # максимальная ёмкость
        self.count = 0  # реальное количество точек
        self.x = np.zeros(capacity, int)
        self.y = np.zeros(capacity, int)
        self.dist = np.zeros(capacity, float)  # расстояние от предыдущей точки (у первой точки, очевидно, 0)
        self.az = np.zeros(capacity, float)  # азимут от предыдущей точки (у первой точки - 0)
        self.bounds = BBox()

    def append(self, x: float, y: float):
        self.x[self.count] = x
        self.y[self.count] = y
        if self.count > 0:
            self.dist[self.count] = dist(self.x[self.count - 1], self.y[self.count - 1], x, y)
            self.az[self.count] = angle180(self.x[self.count - 1], self.y[self.count - 1], x, y)
        self.count += 1
        self.bounds.add(x, y)

    def set(self, idx: int, x: float, y: float):
        if idx >= 0 and idx < self.count:
            self.x[idx] = x
            self.y[idx] = y
            if idx > 0:
                self.dist[idx] = dist(self.x[idx - 1], self.y[idx - 1], x, y)
                self.az[idx] = angle180(self.x[idx - 1], self.y[idx - 1], x, y)
            self.bounds.add(x, y)
        else:
            raise Exception("Point cache index out of bounds")

    def compact(self):
        self.x = np.resize(self.x, self.count)
        self.y = np.resize(self.y, self.count)
        self.dist = np.resize(self.dist, self.count)
        self.az = np.resize(self.az, self.count)
        self.capacity = self.count


class Cell:
    def __init__(self):
        self.count = 0
        self.mark = 0
        self.profile = 0
        self.azimuth = 0
        self.idx1 = -1 # индекс из массива Row.points первой точки в ячейке
        self.idx2 = -1 # индекс из массива Row.points последней точки в ячейке

class Row:
    def __init__(self, xmin, xmax, cellSize):
        width = xmax - xmin
        self.cells = [Cell() for x in range(math.ceil(width / cellSize))]
        self.width = math.ceil(width / cellSize) * cellSize  # длина строки в метрах
        self.xmin = xmin
        self.xmax = xmin + self.width
        self.cellSize = cellSize  # ширина ячейки в метрах
        self.count = 0  # количество точек в строке
        self.filledCount = 0  # количество непустых ячеек в строке
        self.points = []

    def cellIdx(self, x) -> int:
        return int((x - self.xmin) // self.cellSize)

    def add(self, x, g):
        if x >= self.xmin and x < self.xmax:
            self.points.append((x, g))
            # bisect.insort(self.points, (x, g), key=lambda r: r[0]) # нет в Python 3.9
            # idx = self.cellIdx(x)
            # self.cells[idx].add(g)
            self.count += 1
            # if self.cells[idx].count == 1: self.filledCount += 1

    def complete(self, cache):
        # присвоение ячейкам диапазонов входящих в них точек
        #self.points = np.sort(self.points, 0)
        self.points.sort(key=lambda r: r[0])
        ii = 0
        prev = -1
        az = -1
        prev_idx = -1
        for x, i in self.points:
            idx = self.cellIdx(x)
            if idx != prev_idx:
                if prev_idx >= 0:
                    self.cells[prev_idx].azimuth = az / self.cells[prev_idx].count
                self.cells[idx].idx1 = ii
                self.filledCount += 1
                prev = i
                az = 0
            else:
                az += angle180(cache.x[i], cache.y[i], cache.x[prev], cache.y[prev])
                prev = i
            self.cells[idx].idx2 = ii
            self.cells[idx].count += 1
            prev_idx = idx
            ii += 1

# содержит сортированный список точек, разбитых по строкам и ячейкам для ускорения доступа.
class Matrix:
    def __init__(self, xmin, ymin, xmax, ymax, cell_width, cell_height):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = math.ceil((xmax - xmin) / cell_width) * cell_width + xmin
        self.ymax = math.ceil((ymax - ymin) / cell_height) * cell_height + ymin
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.rows_count = math.ceil((self.ymax - self.ymin) / self.cell_height)
        self.cols_count = math.ceil((self.xmax - self.xmin) / self.cell_width)
        self.rows = [Row(self.xmin, self.xmax, self.cell_width) for x in range(self.rows_count)]
        self.count = 0

    def rowIdx(self, y) -> int:
        return int((y - self.ymin) // self.cell_height)

    def add(self, x, y, g):
        if y >= self.ymin and y < self.ymax:
            idx = self.rowIdx(y)
            self.rows[idx].add(x, g)
            self.count += 1

    def complete(self, cache):
        for i in range(self.rows_count):
            self.rows[i].complete(cache)


    def sortRows(self):
        res = [(i, self.rows[i].filledCount) for i in range(self.rows_count)]
        return sorted(res, key=lambda c: c[1], reverse=True)

    # проверяет, заполнена ли ячейка или смежные с ней - для включения в профиль
    def isCandidate(self, row, col, strict=False) -> bool:
        # подразумевается, что границы матрицы взяты с запасом и проверка индексов не требуется
        if strict:
            return self.rows[row].cells[col].count > 0
        else:
            return self.rows[row].cells[col].count > 0 or self.rows[row - 1].cells[col].count > 0 or \
                   self.rows[row + 1].cells[col].count > 0

    def isFirstCandidate(self, row, col) -> bool:
        return self.rows[row].cells[col].count > 0

    # проверяет, не включена ли уже ячейка или смежные с ней в профиль
    def canUse(self, row, col) -> bool:
        return self.rows[row].cells[col].mark == 0 and self.rows[row - 1].cells[col].mark == 0 and \
               self.rows[row + 1].cells[col].mark == 0

    def mark(self, row, col, strict=False):
        self.rows[row].cells[col].mark = 1 if self.rows[row].cells[col].count > 0 else 0
        if not strict:
            self.rows[row - 1].cells[col].mark = 1 if self.rows[row - 1].cells[col].count > 0 else 0
            self.rows[row + 1].cells[col].mark = 1 if self.rows[row + 1].cells[col].count > 0 else 0

