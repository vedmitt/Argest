# -*- coding: utf-8 -*-

import math

# вычисление азимута на плоскости
def azimuth(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    if dist > 0:
        beta = math.degrees(math.acos(math.fabs(dx) / dist))
        if dx > 0:
            if dy < 0:
                res = 270 + beta
            else:
                res = 270 - beta
        else:
            if dy < 0:
                res = 90 - beta
            else:
                res = 90 + beta
        return res
    else:
        return float("inf")

def azimuth180(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    if dist > 0:
        beta = math.degrees(math.acos(math.fabs(dx) / dist))
        if dx > 0:
            if dy < 0:
                res = 270 + beta
            else:
                res = 270 - beta
        else:
            if dy < 0:
                res = 90 - beta
            else:
                res = 90 + beta
        if res >= 180: res = res - 180
        return res
    else:
        return float("inf")

def angle180(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    if dist > 0:
        beta = math.degrees(math.acos(math.fabs(dx) / dist))
        if beta >= 180: beta -= 180
        return beta
    return None

# вращение точки относительно заданного центра
def rotate(px, py, cx, cy, angle):
    nx = (px - cx) * math.cos(angle) - (py - cy) * math.sin(angle) + cx
    ny = (px - cx) * math.sin(angle) + (py - cy) * math.cos(angle) + cy
    return nx, ny

# декартово расстояние между двумя точками
def dist(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

class BBox:
    def __init__(self):
        self.xmax = float("-inf")
        self.ymax = float("-inf")
        self.xmin = float("inf")
        self.ymin = float("inf")
        self.cx = None
        self.cy = None

    def add(self, x: float, y: float):
        self.xmax = max(self.xmax, x)
        self.ymax = max(self.ymax, y)
        self.xmin = min(self.xmin, x)
        self.ymin = min(self.ymin, y)
        self.cx = self.xmin + (self.xmax - self.xmin) / 2
        self.cy = self.ymin + (self.ymax - self.ymin) / 2
