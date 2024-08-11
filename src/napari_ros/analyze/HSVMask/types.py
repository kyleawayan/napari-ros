from typing import TypedDict
from napari.layers import Layer


class HSVMaskConfigType(TypedDict):
    layer: Layer
    crop: "list[int]"
    secondCropBox: "list[int]"
    mirror: bool
    h: "list[float, float]"
    s: "list[float, float]"
    v: "list[float, float]"
    pixelsInUnit: int
    cmApart: float
    fps: float
