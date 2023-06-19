import numpy as np
from .rgbToHsvLookup import load_rgb_to_hsv_lookup
from .flameMask import getFlameMask, getBinaryContours


class HSVMaskAnalyzer:
    def __init__(self):
        self.rgbToHsvLookup = load_rgb_to_hsv_lookup()

    def getMaskAndContours(
        self,
        h: tuple[float, float],  # min, max, from 0 to 1
        s: tuple[float, float],
        v: tuple[float, float],
        areaFilter: int,
        frame: np.ndarray,
    ):
        # Convert to HSV
        hsvFrame = self.rgbToHsvLookup[frame[0], frame[1], frame[2]]

        # By this point, hsvFrame is HSV scaled 0 to 1

        # Run getFlameMask
        mask = getFlameMask(h, s, v, hsvFrame)

        # Get contours
        contours = getBinaryContours(mask)

        return mask, contours
