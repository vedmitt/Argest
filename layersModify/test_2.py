import math


def rotateTransform(x, y, deg_ccw):
    angle = math.radians(-deg_ccw)

    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)

    new_w = cos_theta * x - sin_theta * y
    new_h = sin_theta * x + cos_theta * y

    return new_w, new_h

print(rotateTransform(-2, -1, 110))