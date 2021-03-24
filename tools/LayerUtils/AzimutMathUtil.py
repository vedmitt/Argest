import math

from osgeo import ogr


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

    def getAzimuth(self, feat_list, numOfRes, start_point):
        i = 0
        res = []
        for i in range(numOfRes):
            azimuth = AzimutMathUtil().azimutCalc(
                [feat_list[start_point].geometry().GetX(), feat_list[start_point].geometry().GetY()],
                [feat_list[start_point + i].geometry().GetX(),
                 feat_list[start_point + i].geometry().GetY()])
            res.append(azimuth)
            i += 1
        return res

    def distanceCalc(self, x1, x2):
        dX = x2[0] - x1[0]
        dY = x2[1] - x1[1]
        dist = math.sqrt((dX * dX) + (dY * dY))
        return dist

    def averageDist(self, feat_list):
        av_dist = 0
        dist_list = []
        i = 0
        while i + 1 < len(feat_list):
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
        av_az = 0
        az_list = []
        i = 0
        while i + 1 < len(feat_list):
            dist = self.azimutCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
                                   [feat_list[i + 1].geometry().GetX(),
                                    feat_list[i + 1].geometry().GetY()])
            az_list.append(dist)
            i += 1

        if len(az_list) != 0:
            for item in az_list:
                av_az = av_az + item

            av_az = av_az / len(az_list)
        return av_az

    def rotateTransform(self, w, h, deg_ccw):
        sx = sy = 1
        angle = math.radians(-deg_ccw)

        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)

        scaled_w, scaled_h = w * sx, h * sy

        new_w = int(math.ceil(math.fabs(cos_theta * scaled_w) + math.fabs(sin_theta * scaled_h)))
        new_h = int(math.ceil(math.fabs(sin_theta * scaled_w) + math.fabs(cos_theta * scaled_h)))

        cx = w / 2.
        cy = h / 2.
        tx = new_w / 2.
        ty = new_h / 2.

        a = cos_theta / sx
        b = sin_theta / sx
        c = cx - tx * a - ty * b
        d = -sin_theta / sy
        e = cos_theta / sy
        f = cy - tx * d - ty * e

        return [new_w, new_h]
