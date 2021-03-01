import math


class AzimutMathUtil:
    def __init__(self):
        pass

    def azimutCalc(self, x1, x2):
        dX = x2[0] - x1[0]
        dY = x2[1] - x1[1]
        dist = math.sqrt((dX * dX) + (dY * dY))
        dXa = math.fabs(dX)
        if dist != 0:
            beta = math.degrees(math.acos(dXa / dist))
            if (dX > 0):
                if (dY < 0):
                    angle = 270 + beta
                else:
                    angle = 270 - beta
            else:
                if (dY < 0):
                    angle = 90 - beta
                else:
                    angle = 90 + beta
            return angle
        else:
            return 0

    def distanceCalc(self, x1, x2):
        dX = x2[0] - x1[0]
        dY = x2[1] - x1[1]
        dist = math.sqrt((dX * dX) + (dY * dY))
        return dist