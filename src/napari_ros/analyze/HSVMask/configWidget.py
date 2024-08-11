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

import json
import os

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
            secondCropBox = new["secondCropBox"]
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

        # If mirror, flip the frame in the napari image layer
        if mirror:
            layer.affine = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, layer.data.shape[2]], [0.0, 0.0, 1.0]])
        else:
            layer.affine = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])

        # Get the current frame
        rawFrame = layer.data[frameNumber, :, :, :]

        frame, mask, highestXPos, boundingBoxWithSecondCropBox, maskWithSecondCropBox, lowestXPos, flameTipCoordinates = analyzer.completelyAnalyzeFrame(
            rawFrame, crop, secondCropBox, mirror, h, s, v
        )

        # Now lets add annotations

        # Mask image layer
        previewMask = np.zeros((rawFrame.shape[0], rawFrame.shape[1]))
        start_point = (secondCropBox[0], secondCropBox[2])

        # Calculate the available space in previewMask from the start_point
        available_height = previewMask.shape[0] - start_point[0]
        available_width = previewMask.shape[1] - start_point[1]

        # Clip the mask if it exceeds the available space
        clipped_mask = maskWithSecondCropBox[:min(maskWithSecondCropBox.shape[0], available_height), 
                                            :min(maskWithSecondCropBox.shape[1], available_width)]

        # Place the clipped mask into the previewMask
        previewMask[
            start_point[0]:start_point[0]+clipped_mask.shape[0],
            start_point[1]:start_point[1]+clipped_mask.shape[1]
        ] = clipped_mask

        # Preview the mask
        maskWithSecondCrop = (
            previewMask,
            {
                "name": "Mask WITH SECOND CROP BOX",
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
            {"name": "Crop", "edge_color": "white", "face_color": "transparent", "edge_width": 2, "opacity": 1},
            "shapes",
        )

        # Draw a box around the crop WITH SECOND CROP BOX
        boxVerticies = np.array(
            [
                [secondCropBox[0], secondCropBox[2]],
                [secondCropBox[0], secondCropBox[3]],
                [secondCropBox[1], secondCropBox[3]],
                [secondCropBox[1], secondCropBox[2]],
            ]
        )
        cropLayerWithSecondCropBox = (
            boxVerticies,
            {"name": "Crop ONLY X", "edge_color": "grey", "face_color": "transparent", "edge_width": 2, "opacity": 1},
            "shapes",
        )

        # Draw a red line at the highest X pos
        highestXPosLayer = (
            np.array(
                [
                    [crop[0], highestXPos + crop[2]],
                    [rawFrame.shape[0], highestXPos + crop[2]],
                ]
            ),
            {
                "name": "Highest X Pos",
                "edge_color": "red",
                "shape_type": "line",
                "edge_width": 5,
                "opacity": 1,
            },
            "Shapes",
        )

        # Draw a magenta line at the lowest X pos
        lowestXPosLayer = (
            np.array(
                [
                    [crop[0], lowestXPos + crop[2]],
                    [rawFrame.shape[0], lowestXPos + crop[2]],
                ]
            ),
            {
                "name": "Lowest X Pos",
                "edge_color": "magenta",
                "shape_type": "line",
                "edge_width": 5,
                "opacity": 1,
            },
            "Shapes",
        )

        # Draw a blue box around the bounding box WITH SECOND CROP BOX offset
        boundingBoxWithSecondCropBoxLayer = (
            np.array(
                [
                    [boundingBoxWithSecondCropBox[0] + (secondCropBox[0]), boundingBoxWithSecondCropBox[2] + secondCropBox[2]],
                    [boundingBoxWithSecondCropBox[0] + (secondCropBox[0]), boundingBoxWithSecondCropBox[3] + secondCropBox[2]],
                    [boundingBoxWithSecondCropBox[1] + (secondCropBox[0]), boundingBoxWithSecondCropBox[3] + secondCropBox[2]],
                    [boundingBoxWithSecondCropBox[1] + (secondCropBox[0]), boundingBoxWithSecondCropBox[2] + secondCropBox[2]]
                ]
            ),
            {
                "name": "Bounding Box WITH SECOND CROP BOX",
                "edge_color": "blue",
                "face_color": "transparent",
                "edge_width": 2,
                "opacity": 1,
            },
            "shapes",
        )

        # Draw a purple point at the flame tip
        flameTipLayer = (
            np.array(
                [
                    [flameTipCoordinates[1] + (secondCropBox[0]), flameTipCoordinates[0] + secondCropBox[2]],
                ]
            ),
            {
                "name": "Flame Tip",
                "face_color": "purple",
                "size": 20,
                "opacity": 1,
            },
            "points",
        )

        annotatedLayers = [maskWithSecondCrop, cropLayerWithSecondCropBox, cropLayer, highestXPosLayer, boundingBoxWithSecondCropBoxLayer, lowestXPosLayer, flameTipLayer]


def calculateEstimatedPlateWidthCm(
    cropWidth: int,
    pixelsBetweenTwoMarkers: float,
    cmBetweenTwoMarkers: int,
):
    pixelsPerCm = pixelsBetweenTwoMarkers / cmBetweenTwoMarkers
    estimatedPlateWidthCm = round(cropWidth / pixelsPerCm, 2)
    return estimatedPlateWidthCm

def fetchConfigFromUserSettings(path: str):
    # Check if the config file exists
    if not os.path.exists(path):
        return None
    
    with open(path, "r") as f:
        config = json.load(f)
        return config

# TODO: Use napari settings or some other better persistent storage
def saveConfigToUserSettings(config: HSVMaskConfigType, path: str):
    # Ignore layer
    config.pop("layer", None)

    # For now just save as a JSON file
    with open(path, "w") as f:
        json.dump(config, f, indent=4)

class HSVMaskConfigWidget(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._viewer = parent._viewer

        # Will be changed by dims.events.current_step
        self.currentFrameNumber = -1

        # Layer 0 should be the image sequence

        self.imageSequenceDirectory = self._viewer.layers[0].source.path
        self.configFilePath = os.path.join(self.imageSequenceDirectory, os.pardir, "napari_ros_last_config.json")

        self.preloadedConfig = fetchConfigFromUserSettings(self.configFilePath)

        self.config: HSVMaskConfigType = {
            "layer": self._viewer.layers[0],
            "crop": [960, 987, 511, 1496],
            "secondCropBox": [360, 987, 511, 1496],
            "mirror": True,
            "h": [0.0, 0.32407407407407407],
            "s": [0.0, 0.6620370370370371],
            "v": [0.9, 1.0],
            "pixelsInUnit": 104,
            "cmApart": 4.5,
            "fps": 59.94
        }

        # If preloaded config, merge it with the default config
        if self.preloadedConfig is not None:
            self.config = {**self.config, **self.preloadedConfig}

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
        # Save config
        saveConfigToUserSettings(self.config, self.configFilePath)

        # Run analysis
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