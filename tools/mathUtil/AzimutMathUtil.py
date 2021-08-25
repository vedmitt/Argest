import math

from .DataTimeUtil import DataTimeUtil


class AzimutMathUtil:

    def __init__(self):
        pass

    def getMax(self, listOfValues):
        return max(listOfValues)

    def getMin(self, listOfValues):
        return min(listOfValues)

    def azimutCalc(self, x1, x2):
        dX = x2[0] - x1[0]
        dY = x2[1] - x1[1]
        dist = math.sqrt((dX * dX) + (dY * dY))
        dXa = math.fabs(dX)
        if dist != 0:
            beta = math.degrees(math.acos(dXa / dist))
            if (dX < 0):
                if (dY > 0):
                    angle = 270 + beta
                else:
                    angle = 270 - beta
            else:
                if (dY > 0):
                    angle = 90 - beta
                else:
                    angle = 90 + beta
            return angle
        else:
            return 0

    def getSpeed(self, prev_i, curr_i):
        dist = self.getDistance(prev_i, curr_i)
        period = DataTimeUtil(curr_i).getDate() - DataTimeUtil(prev_i).getDate()

        if period.total_seconds() != 0:
            speed = dist / period.total_seconds()
            return speed
        else:
            return 99999

    def getAzimuth(self, prev_i, curr_i):
        azimuth = AzimutMathUtil().azimutCalc([prev_i.getGeometry()[0], prev_i.getGeometry()[1]],
                                              [curr_i.getGeometry()[0], curr_i.getGeometry()[1]])
        return azimuth

    def getDistance(self, prev_i, curr_i):
        dist = AzimutMathUtil().distanceCalc([prev_i.getGeometry()[0], prev_i.getGeometry()[1]],
                                             [curr_i.getGeometry()[0], curr_i.getGeometry()[1]])
        return dist

    def distanceCalc(self, x1, x2):
        dX = x2[0] - x1[0]
        dY = x2[1] - x1[1]
        dist = math.sqrt((dX * dX) + (dY * dY))
        return dist

    def calcTargetAzimuth(self, feat_list, isNormal=True):
        step = 10
        res = []
        i = 1
        prev_ind = 0
        while i < feat_list.featureCount():
            a = self.getAzimuth(feat_list.getFeature(prev_ind), feat_list.getFeature(i))
            z = int((a + step / 2) % 360 // step) * 10
            res.append(z)

            prev_ind = i
            i += 1

        targetAzimuth = max(set(res), key=res.count)
        if isNormal:
            if targetAzimuth > 180:
                targetAzimuth -= 180
        return targetAzimuth

if __name__ == '__main__':
    az = AzimutMathUtil()
