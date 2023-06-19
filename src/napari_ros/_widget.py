"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING
from typing import List

import numpy as np
from magicgui import magic_factory
from magicgui.widgets import Label
from enum import Enum
from .analyze.HSVMask.HSVMaskAnalyzer import HSVMaskAnalyzer
from .analyze.HSVMask.drawUtils import offsetContoursBigArrayByCrop

if TYPE_CHECKING:
    import napari

from napari.layers import Layer
from napari.types import LayerDataTuple

analyzer = HSVMaskAnalyzer()


class Methods(Enum):
    HSVMask = 0


def calculateEstimatedPlateWidthCmAndUpdateLabelAndSetLabel(
    cropWidth: int,
    pixelsBetweenTwoMarkers: float,
    cmBetweenTwoMarkers: int,
    label: Label,
):
    pixelsPerCm = pixelsBetweenTwoMarkers / cmBetweenTwoMarkers
    estimatedPlateWidthCm = round(cropWidth / pixelsPerCm, 2)
    label.value = estimatedPlateWidthCm


def _on_init(widget):
    widget.changed.connect(
        lambda x: calculateEstimatedPlateWidthCmAndUpdateLabelAndSetLabel(
            widget.crop.value[2] - widget.crop.value[0],
            widget.pixelsBetweenTwoMarkers.value,
            widget.cmBetweenTwoMarkers.value,
            widget.estimatedPlateWidthCm,
        )
    )


hsvWidgetConfig = {
    "widget_type": "FloatRangeSlider",
    "min": 0,
    "max": 1,
    "step": 0.01,
}


@magic_factory(
    auto_call=True,
    h=hsvWidgetConfig,
    s=hsvWidgetConfig,
    v=hsvWidgetConfig,
    crop={"options": {"max": 2000, "step": 1}, "layout": "vertical"},
    estimatedPlateWidthCm={"widget_type": "Label"},
    widget_init=_on_init,
)
def config_magic_widget(
    layer: Layer,
    method=Methods.HSVMask,
    h=(0.00, 0.38),
    s=(0.49, 0.80),
    v=(0.86, 1.00),
    crop=[800, 1000, 400, 1511],  # top, bottom, left, right
    areaFilter=10,
    pixelsBetweenTwoMarkers=10,
    cmBetweenTwoMarkers=5.00,
    mirror=False,
    estimatedPlateWidthCm=0,
    # estimatedPlateWidth... is a string
    # (since it's a Label widget), so it needs
    # to be converted to a float
) -> List[LayerDataTuple]:

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
    mask, contours = analyzer.getMaskAndContours(h, s, v, areaFilter, frame)

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
    highestXPos = analyzer.getHighestXPosFromContoursBigArray(contoursBigArray)
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

    return [frameLayer, maskLayer, cropLayer, highestXPosLayer]
