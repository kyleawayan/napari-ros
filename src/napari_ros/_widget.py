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

if TYPE_CHECKING:
    import napari


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


@magic_factory(
    auto_call=True,
    h={"widget_type": "RangeSlider", "max": 360, "step": 1},
    s={"widget_type": "RangeSlider", "max": 255, "step": 1},
    v={"widget_type": "RangeSlider", "max": 255, "step": 1},
    crop={"options": {"max": 2000, "step": 1}, "layout": "vertical"},
    estimatedPlateWidthCm={"widget_type": "Label"},
    widget_init=_on_init,
)
def config_magic_widget(
    img_layer: "napari.layers.Image",
    method=Methods.HSVMask,
    h=(0, 360),
    s=(0, 255),
    v=(0, 255),
    crop=[0, 0, 0, 0],
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
        img_layer,
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
