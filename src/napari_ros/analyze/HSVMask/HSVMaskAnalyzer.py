from typing import List
import numpy as np
from skimage.color import rgb2hsv
from .flameMask import getFlameMask, getBinaryContours


class HSVMaskAnalyzer:
    def getMask(
        self,
        h: tuple[float, float],  # min, max, from 0 to 1
        s: tuple[float, float],
        v: tuple[float, float],
        frame: np.ndarray,
    ):
        # Convert to HSV
        hsvFrame = rgb2hsv(frame)

        # By this point, hsvFrame is HSV scaled 0 to 1

        # Run getFlameMask
        mask = getFlameMask(h, s, v, hsvFrame)

        return mask

    def getHighestXPosFromContoursBigArray(self, contoursBigArray: np.ndarray):
        """
        Get the highest x position of the contours.
        Contours should be a numpy array of shape (n, 2): (row, column)
        Note this is not used anymore as just using the boolean mask is more efficient.
        """
        print("WARNING: getHighestXPosFromContoursBigArray is deprecated. Use getHighestXPosFromBinaryMask instead.")
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
    
    def getLowestXPosFromBinaryMask(self, mask: np.ndarray):
        """
        Get the lowest x position using the binary mask.
        mask should be a boolean numpy array.
        """
        # Find the indices of the True values
        indices = np.where(mask)

        # If there are no True values, return 0
        if len(indices[1]) == 0:
            return 0

        # Get the lowest index on the X axis
        return indices[1].min()
    
    def getBoundingBoxFromBinaryMask(self, mask: np.ndarray):
        """
        Get the bounding box of the mask.
        mask should be a boolean numpy array.
        """
        # Find the indices of the True values
        indices = np.where(mask)

        # If there are no True values, return 0
        if len(indices[1]) == 0:
            return [0, 0, 0, 0]

        # Get the bounding box
        return [
            indices[0].min(),
            indices[0].max(),
            indices[1].min(),
            indices[1].max(),
        ]
    
    def getFlameTipFromBinaryMaskAndBoundaryBox(self, mask: np.ndarray, boundaryBoxMaxY: int) -> list[int]:
        """
        Get the flame tip coordinates by taking the boundary box max y,
        and finding the pixel with the highest x value in that row.
        """
        # Get the indices of the True values
        indices = np.where(mask)

        # If there are no True values, return 0
        if len(indices[1]) == 0:
            return [0, 0]

        # Get the indices where the y value is the boundaryBoxMaxY
        indicesMaxY = np.where(indices[0] == boundaryBoxMaxY)

        # If there are no True values, return 0
        if len(indicesMaxY[0]) == 0:
            return [0, 0]

        # Get the highest x value in the row
        return [indices[1][indicesMaxY[0]].max(), boundaryBoxMaxY]

    def completelyAnalyzeFrame(
        self,
        frame: np.ndarray,
        crop: List[int],
        secondCropBox: List[int],
        mirror: bool,
        h: tuple[float, float],
        s: tuple[float, float],
        v: tuple[float, float],
    ):
        # Mirror the frame if needed
        if mirror:
            frame = np.flip(frame, axis=1)

        frameWithSecondCropBox = frame[
            secondCropBox[0] : secondCropBox[1],
            secondCropBox[2] : secondCropBox[3],
            :,
        ]

        maskWithSecondCropBox = self.getMask(h, s, v, frameWithSecondCropBox) 

        # Crop the frame
        frame = frame[
            crop[0] : crop[1],
            crop[2] : crop[3],
            :,
        ]

        # By this point, frame should be an RGB scaled 0-255

        # Get mask and contours
        # TODO: Area filter
        mask = self.getMask(h, s, v, frame)

        # Get bounding box of mask WITHOUT CROP
        boundingBoxWithSecondCropBox = self.getBoundingBoxFromBinaryMask(maskWithSecondCropBox)

        # Get the flame tip coordinates
        flameTipCoordinates = self.getFlameTipFromBinaryMaskAndBoundaryBox(maskWithSecondCropBox, boundingBoxWithSecondCropBox[0])

        # Get the highest x position of the mask
        highestXPos = self.getHighestXPosFromBinaryMask(mask)

        # Get the lowest x position of the mask
        lowestXPos = self.getLowestXPosFromBinaryMask(mask)

        return frame, mask, highestXPos, boundingBoxWithSecondCropBox, maskWithSecondCropBox, lowestXPos, flameTipCoordinates
