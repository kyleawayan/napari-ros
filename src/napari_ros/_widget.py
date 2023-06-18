"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING

from magicgui import magic_factory
from magicgui.widgets import Label
from enum import Enum
from .analyze.HSVMask.HSVMaskAnalyzer import HSVMaskAnalyzer

if TYPE_CHECKING:
    import napari

from napari.layers import Layer

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
    h=(0.00, 1.00),
    s=(0.00, 1.00),
    v=(0.00, 1.00),
    crop=[428, 832, 1511, 924],
    areaFilter=10,
    pixelsBetweenTwoMarkers=10,
    cmBetweenTwoMarkers=5.00,
    mirror=False,
    estimatedPlateWidthCm=0,
    # estimatedPlateWidth... is a string
    # (since it's a Label widget), so it needs
    # to be converted to a float
):
    print(
        layer,
        method,
        h,
        s,
        v,
        crop,
        areaFilter,
        pixelsBetweenTwoMarkers,
        cmBetweenTwoMarkers,
        mirror,
        estimatedPlateWidthCm,
    )

    # Check if the image is empty
    if layer is None:
        return

    # Get the current frame the napari viewer is on
    frameNumber = int(layer._dims_point[0])

    # Get the current frame
    frame = layer.data[frameNumber, :, :, :]

    # Crop the frame
    frame = frame[
        crop[0] : crop[2],
        crop[1] : crop[3],
        :,
    ]
    print(frame.shape)

    # By this point, frame should be an RGB scaled 0-255

    # Get mask and contours
    # TODO: Area filter
    mask, contours = analyzer.getMaskAndContours(h, s, v, areaFilter, frame)

    print(mask, contours)
