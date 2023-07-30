import numpy as np


def load_rgb_to_hsv_lookup():
    """
    See `notebooks/createRgbToHsvLookup.ipynb`
    """
    # Load the lookup table from a file
    return np.load(
        "/Users/kyle/Documents/Projects/napari-ros/src/napari_ros/precomputed/rgbToHsv.npy"
    )
