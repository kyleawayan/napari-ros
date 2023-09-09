import numpy as np
from skimage import measure


def getFlameMask(
    h: tuple[float, float],
    s: tuple[float, float],
    v: tuple[float, float],
    hsvFrame: np.ndarray,
):
    """
    Get the mask of the flame using the HSV min and max values. Takes in a frame in HSV format, scaled 0 to 1.
    Outputs True and False values. frame needs to be converted to HSV first.
    """
    # https://scikit-image.org/docs/stable/auto_examples/color_exposure/plot_rgb_to_hsv.html#id2
    hsv_img = hsvFrame

    hue_img = hsv_img[:, :, 0]
    sat_img = hsv_img[:, :, 1]
    value_img = hsv_img[:, :, 2]

    # Min and max values are 0-1 scale
    hue_min = h[0]
    hue_max = h[1]
    sat_min = s[0]
    sat_max = s[1]
    value_min = v[0]
    value_max = v[1]

    return (
        (hue_img >= hue_min)
        & (hue_img <= hue_max)
        & (sat_img >= sat_min)
        & (sat_img <= sat_max)
        & (value_img >= value_min)
        & (value_img <= value_max)
    )


def getBinaryContours(frame: np.ndarray, constant=0.8):
    """
    Get the contours of a binary image.
    Run getFlameMask() first and pass the output to this function.
    """
    return measure.find_contours(frame, constant)
