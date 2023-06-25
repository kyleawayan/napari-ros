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
        areaFilter: int,
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
        """
        return contoursBigArray[:, 1].max()

    def completelyAnalyzeFrame(
        self,
        frame: np.ndarray,
        crop: List[int],
        mirror: bool,
        h: tuple[float, float],
        s: tuple[float, float],
        v: tuple[float, float],
        areaFilter: int,
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
        mask, contours = self.getMaskAndContours(h, s, v, areaFilter, frame)

        if contours == []:
            # No contours found,
            # so we just return a single point at (0, 0)
            # so np.concatenate doesn't fail
            contours = np.array([[[0, 0]]])

        # Contours is a list of numpy arrays,
        # and napari needs a single numpy array for
        # the points layer, so we concatenate the list
        # of numpy arrays into a single numpy array
        contoursBigArray = np.concatenate(contours, axis=0)

        # Get the highest x position of the contours
        highestXPos = self.getHighestXPosFromContoursBigArray(contoursBigArray)

        return frame, mask, contours, contoursBigArray, highestXPos
