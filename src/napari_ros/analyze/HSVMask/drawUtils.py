from typing import List
import numpy as np


def offsetContoursBigArrayByCrop(contours: np.ndarray, crop: List[int]):
    """
    Offsets the contours by the crop values.
    Does not work when mirrored.
    Crop should be [top, bottom, left, right]
    Contours should be a numpy array of shape (n, 2): (row, column)
    """

    # Copy numpy array so we don't modify the original
    contours = np.copy(contours)

    contours[:, 0] += crop[0]
    contours[:, 1] += crop[2]

    return contours
