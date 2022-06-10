import functools
import math


def normalize_azimuth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        azimuth = func(*args, **kwargs)
        if azimuth > 180:
            azimuth -= 180
        return azimuth

    return wrapper


class Math:

    # @normalize_azimuth
    def azimuth_calc(self, x1, x2):
        """AZIMUTH Calculation.
        :x1, x2: coordinates of points
        :type x1, x2: tuples
        Returns AZIMUTH angle in degrees"""

        dX = x2[0] - x1[0]
        dY = x2[1] - x1[1]
        dist = math.sqrt((dX * dX) + (dY * dY))
        dXa = math.fabs(dX)
        if dist != 0:
            beta = math.degrees(math.acos(dXa / dist))
            if dX < 0:
                if dY > 0:
                    angle = 270 + beta
                else:
                    angle = 270 - beta
            else:
                if dY > 0:
                    angle = 90 - beta
                else:
                    angle = 90 + beta
            return angle
        else:
            return 0

    def check_bounds(self, azimuth):
        if azimuth < 0:
            return 360+azimuth
        elif azimuth > 360:
            return azimuth-360
        else:
            return azimuth

    def build_bounds(self, bound):
        b = [self.check_bounds(bound[0]), self.check_bounds(bound[1])]
        if b[0] > b[1]:
            return 0, b[1], b[0], 360
        else:
            return b[0], b[1]
