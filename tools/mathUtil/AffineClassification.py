import math


class AffineClassification:
    def __init__(self, guiUtil):
        self.guiUtil = guiUtil

    def rotateTransform(self, x, y, deg_ccw):
        angle = math.radians(-deg_ccw)

        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)

        new_w = cos_theta * x - sin_theta * y
        new_h = sin_theta * x + cos_theta * y

        return new_w, new_h

    def affineCoordinate(self, feat_list, targetAzimuth):
        new_coordinates = []
        angle = 90 - targetAzimuth
        Ox = feat_list[0].geometry().GetX()
        Oy = feat_list[0].geometry().GetY()

        for feat in feat_list:
            fg = feat.geometry()
            dx = fg.GetX() - Ox
            dy = fg.GetY() - Oy
            new_x, new_y = self.rotateTransform(dx, dy, angle)
            new_coordinates.append([new_x, new_y])

        return new_coordinates
