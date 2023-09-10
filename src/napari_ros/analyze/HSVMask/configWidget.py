import time
import numpy as np
from typing import List

from napari.layers import Layer
from napari.types import LayerDataTuple
from napari.qt.threading import thread_worker

from .HSVMaskAnalyzer import HSVMaskAnalyzer
from .analyzeModal import AnalyzeModal
from .parametersWidget import HSVMaskParametersWidget
from .types import HSVMaskConfigType

from qtpy.QtWidgets import QWidget, QVBoxLayout, QPushButton
from qtpy.QtCore import QTimer

analyzer = HSVMaskAnalyzer()


def calculateEstimatedPlateWidthCm(
    cropWidth: int,
    pixelsBetweenTwoMarkers: float,
    cmBetweenTwoMarkers: int,
):
    pixelsPerCm = pixelsBetweenTwoMarkers / cmBetweenTwoMarkers
    estimatedPlateWidthCm = round(cropWidth / pixelsPerCm, 2)
    return estimatedPlateWidthCm


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
            frameNumber = new["currentFrameNumber"]
        except:
            continue

        # Check if the image is empty
        if layer is None:
            continue

        # Get the current frame
        rawFrame = layer.data[frameNumber, :, :, :]

        frame, mask, highestXPos = analyzer.completelyAnalyzeFrame(
            rawFrame, crop, mirror, h, s, v
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


def calculateEstimatedPlateWidthCm(
    cropWidth: int,
    pixelsBetweenTwoMarkers: float,
    cmBetweenTwoMarkers: int,
):
    pixelsPerCm = pixelsBetweenTwoMarkers / cmBetweenTwoMarkers
    estimatedPlateWidthCm = round(cropWidth / pixelsPerCm, 2)
    return estimatedPlateWidthCm


class HSVMaskConfigWidget(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._viewer = parent._viewer

        # Will be changed by dims.events.current_step
        self.currentFrameNumber = -1

        # Layer 0 should be the image sequence

        self.config: HSVMaskConfigType = {
            "layer": self._viewer.layers[0],
            "crop": [960, 987, 511, 1496],
            "mirror": True,
            "h": [0.0, 0.32407407407407407],
            "s": [0.0, 0.6620370370370371],
            "v": [0.9, 1.0],
            "pixelsInUnit": 104,
            "cmApart": 4.5,
            "fps": 59.94
        }

        self.imageSequenceDirectory = self._viewer.layers[0].source.path

        self.worker = runHsvMaskAndReturnAnnotations()
        self.worker.yielded.connect(self.on_yielded)
        self.worker.start()

        self.currentFrameNumber = self._viewer.dims.current_step[0]
        self._viewer.dims.events.current_step.connect(self.onFrameChange)

        layout = QVBoxLayout()

        # Add parameters widget
        parametersWidget = HSVMaskParametersWidget(self)

        # Note this signal does not send anything.
        # The config is passed by reference already
        # and can be edited straight from the widget
        parametersWidget.valueChanged.connect(self.workerFrameAnalysis)

        layout.addWidget(parametersWidget)

        # Create "Analyze" button
        analyzeButton = QPushButton("Analyze")
        analyzeButton.clicked.connect(self.runAnalysis)
        layout.addWidget(analyzeButton)

        # Send config to worker to create initial annotations
        # Add a delay so the worker has time to start
        QTimer.singleShot(2000, self.workerFrameAnalysis)

        self.setLayout(layout)

    def runAnalysis(self):
        dialog = AnalyzeModal(self)
        dialog.exec_()

    def onFrameChange(self, event):
        self.currentFrameNumber = event.value[0]
        self.workerFrameAnalysis()

    def workerFrameAnalysis(self):
        # Add current frame number to config dict, so we can send it to the worker
        configToSend = self.config.copy()
        configToSend["currentFrameNumber"] = self.currentFrameNumber
        self.worker.send(configToSend)
        self.worker.resume()

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

            self._viewer.add_layer(Layer.create(*returnedLayerTuple))