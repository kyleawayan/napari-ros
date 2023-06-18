import numpy as np


def create_rgb_to_hsv_lookup():
    # Define a lookup table with precomputed HSV values for all RGB values
    hsv_lookup = np.empty((256, 256, 256, 3), dtype=np.float32)
    for r in range(256):
        for g in range(256):
            for b in range(256):
                max_value = max(r, g, b)
                min_value = min(r, g, b)
                v = max_value / 255.0
                if max_value == 0:
                    s = 0.0
                    h = 0.0
                else:
                    s = (max_value - min_value) / max_value
                    if max_value == min_value:
                        h = 0.0
                    elif max_value == r:
                        h = (g - b) / (max_value - min_value)
                    elif max_value == g:
                        h = 2 + (b - r) / (max_value - min_value)
                    else:
                        h = 4 + (r - g) / (max_value - min_value)
                    h *= 60.0
                    if h < 0:
                        h += 360.0
                    h /= 360.0
                hsv_lookup[r, g, b] = np.array([h, s, v], dtype=np.float32)
    return hsv_lookup


def load_rgb_to_hsv_lookup():
    # Load the lookup table from a file
    return np.load(
        "/Users/kyle/Documents/Projects/napari-ros/src/napari_ros/precomputed/rgbToHsv.npy"
    )
