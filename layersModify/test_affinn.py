from PIL import Image
import math


def scale_and_rotate_image(im, sx, sy, deg_ccw):
    im_orig = im
    im = Image.new('RGBA', im_orig.size, (255, 255, 255, 255))
    im.paste(im_orig)

    w, h = im.size
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

    return im.transform(
        (new_w, new_h),
        Image.AFFINE,
        (a, b, c, d, e, f),
        resample=Image.BILINEAR
    )

if __name__ == "__main__":
    im = Image.open('test_1.png')
    im = scale_and_rotate_image(im, 1, 1, -29.8)
    im.save('outputpython.png')