"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING
from typing import List

import numpy as np
from enum import Enum
from .analyze.HSVMask.HSVMaskAnalyzer import HSVMaskAnalyzer

if TYPE_CHECKING:
    import napari

from napari.layers import Layer
from napari.viewer import Viewer
from napari.types import LayerDataTuple
from napari.qt.threading import thread_worker
from qtpy.QtWidgets import QWidget, QVBoxLayout, QPushButton

# TODO: Load class based on method
analyzer = HSVMaskAnalyzer()


class Methods(Enum):
    HSVMask = 0


def calculateEstimatedPlateWidthCm(
    cropWidth: int,
    pixelsBetweenTwoMarkers: float,
    cmBetweenTwoMarkers: int,
):
    pixelsPerCm = pixelsBetweenTwoMarkers / cmBetweenTwoMarkers
    estimatedPlateWidthCm = round(cropWidth / pixelsPerCm, 2)
    return estimatedPlateWidthCm


hsvWidgetConfig = {
    "widget_type": "FloatRangeSlider",
    "min": 0,
    "max": 1,
    "step": 0.01,
}

# TODO: Put in another file
@thread_worker
def runHsvMaskAndReturnAnnotations():
    annotatedLayers: List[LayerDataTuple] = []

    while True:
        new = yield annotatedLayers

        try:
            layer = new["layer"]
            crop = new["crop"]
            mirror = new["mirror"]
            h = new["h"]
            s = new["s"]
            v = new["v"]
            areaFilter = new["areaFilter"]
        except:
            continue

        # Check if the image is empty
        if layer is None:
            return

        # Get the current frame the napari viewer is on
        frameNumber = int(layer._dims_point[0])

        # Get the current frame
        rawFrame = layer.data[frameNumber, :, :, :]

        # Crop the frame
        frame = rawFrame[
            crop[0] : crop[1],
            crop[2] : crop[3],
            :,
        ]

        # Mirror the frame if needed
        if mirror:
            frame = np.flip(frame, axis=1)

        # By this point, frame should be an RGB scaled 0-255

        # Preview the frame
        frameLayer = (
            frame,
            {"name": "Frame"},
            "image",
        )

        # Get mask and contours
        # TODO: Area filter
        mask, contours = analyzer.getMaskAndContours(
            h, s, v, areaFilter, frame
        )

        # Preview the mask
        maskLayer = (
            mask,
            {
                "name": "Mask",
                "colormap": "green",
                "contrast_limits": [0, 1],
                "opacity": 0.5,
            },
            "image",
        )

        # Now lets add annotations

        # Draw a box around the crop
        boxVerticies = np.array(
            [
                [crop[0], crop[2]],
                [crop[0], crop[3]],
                [crop[1], crop[3]],
                [crop[1], crop[2]],
            ]
        )
        cropLayer = (
            boxVerticies,
            {"name": "Crop", "edge_color": "white"},
            "shapes",
        )

        if contours == []:
            return [maskLayer, cropLayer]

        # Contours is a list of numpy arrays,
        # and napari needs a single numpy array for
        # the points layer, so we concatenate the list
        # of numpy arrays into a single numpy array
        contoursBigArray = np.concatenate(contours, axis=0)

        # Now the contours
        # Uncomment and add to return to preview contours
        # contoursLayer = (
        #     contoursBigArray,
        #     {"name": "Contours", "face_color": "green"},
        #     "points",
        # )

        # Draw a red line at the highest X pos
        highestXPos = analyzer.getHighestXPosFromContoursBigArray(
            contoursBigArray
        )
        highestXPosLayer = (
            np.array(
                [
                    [0, highestXPos],
                    [frame.shape[0], highestXPos],
                ]
            ),
            {
                "name": "Highest X Pos",
                "edge_color": "red",
                "shape_type": "line",
                "edge_width": 5,
            },
            "Shapes",
        )

        annotatedLayers = [frameLayer, maskLayer, cropLayer, highestXPosLayer]


class ConfigWidget(QWidget):
    def __init__(self, viewer: Viewer):
        super().__init__()
        self._viewer = viewer

        # TODO: Load worker based on method
        self.worker = runHsvMaskAndReturnAnnotations()
        self.worker.yielded.connect(self.on_yielded)
        self.worker.start()

        layout = QVBoxLayout()

        # Create button
        button = QPushButton("Run")
        button.clicked.connect(self.sendSampleConfigToWorker)
        layout.addWidget(button)

        self.setLayout(layout)

    def sendSampleConfigToWorker(self):
        config = {
            "layer": self._viewer.layers[0],
            "crop": [800, 1000, 400, 1511],
            "mirror": False,
            "h": (0.00, 0.38),
            "s": (0.49, 0.80),
            "v": (0.86, 1.00),
            "areaFilter": 10,
        }
        self.send_next_value(config)

    def on_yielded(self, value):
        self.worker.pause()
        # For now lets just put the frame layer
        frameLayer = value[0]
        self._viewer.add_image(frameLayer[0])

    def send_next_value(self, config):
        self.worker.send(config)
        self.worker.resume()
