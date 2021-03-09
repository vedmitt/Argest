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

    def averageDist(self, feat_list):
        av_dist = 0
        dist_list = []
        i = 0
        while i+1 < len(feat_list):
            dist = self.distanceCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
                                     [feat_list[i + 1].geometry().GetX(),
                                      feat_list[i + 1].geometry().GetY()])
            dist_list.append(dist)
            i += 1

        if len(dist_list) != 0:
            for item in dist_list:
                av_dist = av_dist + item

            av_dist = av_dist / len(dist_list)
        return av_dist

    def averageAzimut(self, feat_list):
        az_list = []
        av_az = 0
        for item in feat_list:
            az_list.append(self.azimutCalc(item.geometry().GetX(), item.geometry().GetY()))
        if len(az_list) != 0:
            for i in az_list:
                av_az = av_az + i
            av_az = av_az / len(az_list)
        return av_az
