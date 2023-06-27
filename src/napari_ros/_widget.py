"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING, List, Dict
import time

import numpy as np
from enum import Enum
from .analyze.HSVMask.HSVMaskAnalyzer import HSVMaskAnalyzer
from .analyze.HSVMask.analyzeModal import AnalyzeModal

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
        time.sleep(0.5)
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
            continue

        # Get the current frame the napari viewer is on
        frameNumber = int(layer._dims_point[0])

        # Get the current frame
        rawFrame = layer.data[frameNumber, :, :, :]

        frame, mask, highestXPos = analyzer.completelyAnalyzeFrame(
            rawFrame, crop, mirror, h, s, v, areaFilter
        )

        # Now lets add annotations

        # Preview the frame
        frameLayer = (
            frame,
            {"name": "Frame"},
            "image",
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

        # Draw a red line at the highest X pos
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

        # Sample config
        self.config = {
            "layer": self._viewer.layers[0],
            "crop": [577, 629, 320, 958],
            "mirror": True,
            "h": (0.00, 0.38),
            "s": (0.275, 0.80),
            "v": (0.9, 1.00),
            "areaFilter": 10,
        }
        # TODO: Get from napari
        self.imageSequenceDirectory = "/Users/kyle/Desktop/mock ros videos/DSC_0357_Test_No26_720_2997FPS"

        # TODO: Load worker based on method
        self.worker = runHsvMaskAndReturnAnnotations()
        self.worker.yielded.connect(self.on_yielded)
        self.worker.start()

        self._viewer.dims.events.current_step.connect(self.onFrameChange)

        layout = QVBoxLayout()

        # Create button
        button = QPushButton("Run")
        button.clicked.connect(self.sendSampleConfigToWorker)
        layout.addWidget(button)

        # Create "Analyze" button
        analyzeButton = QPushButton("Analyze")
        analyzeButton.clicked.connect(self.runAnalysis)
        layout.addWidget(analyzeButton)

        self.setLayout(layout)

    def runAnalysis(self):
        dialog = AnalyzeModal(self)
        dialog.exec_()

    def onFrameChange(self, event):
        currentFrameNumber = event.value
        self.sendSampleConfigToWorker()

    def sendSampleConfigToWorker(self):
        self.send_next_value(self.config)

    def on_yielded(self, value):
        self.worker.pause()

        if len(value) == 0:
            return

        currentLayers = self._viewer.layers

        # TODO: Make layer updating more efficient
        # and don't use _add_layer_from_data
        for returnedLayerTuple in value:
            returnedLayerName = returnedLayerTuple[1]["name"]
            foundLayer = False

            for layer in currentLayers:
                if layer.name == returnedLayerName:
                    foundLayer = True
                    layer.data = returnedLayerTuple[0]
                    break

            if foundLayer:
                continue

            self._viewer._add_layer_from_data(*returnedLayerTuple)

    def send_next_value(self, config):
        self.worker.send(config)
        self.worker.resume()
