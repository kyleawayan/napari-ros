"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING
from .analyze.HSVMask.configWidget import HSVMaskConfigWidget

if TYPE_CHECKING:
    import napari

from napari.viewer import Viewer
from qtpy.QtWidgets import QWidget, QVBoxLayout


class ConfigWidget(QWidget):
    def __init__(self, viewer: Viewer):
        super().__init__()
        self._viewer = viewer

        layout = QVBoxLayout()

        # Add config widget (for HSV for now)
        layout.addWidget(HSVMaskConfigWidget(self))

        self.setLayout(layout)
