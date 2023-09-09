from typing import List
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
        frame: np.ndarray,
    ):
        # Convert to HSV
        hsvFrame = self.rgbToHsvLookup[
            frame[..., 0], frame[..., 1], frame[..., 2]
        ]

        # By this point, hsvFrame is HSV scaled 0 to 1

        # Run getFlameMask
        mask = getFlameMask(h, s, v, hsvFrame)

        # Get contours
        contours = getBinaryContours(mask)

        return mask, contours

    def getHighestXPosFromContoursBigArray(self, contoursBigArray: np.ndarray):
        """
        Get the highest x position of the contours.
        Contours should be a numpy array of shape (n, 2): (row, column)
        Note this is not used anymore as just using the boolean mask is more efficient.
        """
        return contoursBigArray[:, 1].max()

    def getHighestXPosFromBinaryMask(self, mask: np.ndarray):
        """
        Get the highest x position using the binary mask.
        mask should be a boolean numpy array.
        """
        # Find the indices of the True values
        indices = np.where(mask)

        # If there are no True values, return 0
        if len(indices[1]) == 0:
            return 0

        # Get the highest index on the X axis
        return indices[1].max()

    def completelyAnalyzeFrame(
        self,
        frame: np.ndarray,
        crop: List[int],
        mirror: bool,
        h: tuple[float, float],
        s: tuple[float, float],
        v: tuple[float, float],
    ):
        # Crop the frame
        frame = frame[
            crop[0] : crop[1],
            crop[2] : crop[3],
            :,
        ]

        # Mirror the frame if needed
        if mirror:
            frame = np.flip(frame, axis=1)

        # By this point, frame should be an RGB scaled 0-255

        # Get mask and contours
        # TODO: Area filter
        mask, contours = self.getMaskAndContours(h, s, v, frame)

        # Get the highest x position of the mask
        highestXPos = self.getHighestXPosFromBinaryMask(mask)

        return frame, mask, highestXPos
