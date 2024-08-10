from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QDoubleSpinBox,
    QGridLayout,
    QSlider,
    QSpinBox,
    QLineEdit
)
from superqt import QLabeledDoubleRangeSlider
import numpy as np
from .types import HSVMaskConfigType
from typing import List
from sympy import S


def calculatePlateWidth(cropWidth: int, cmApart: float, pixelsInUnit: int):
    return round(cropWidth * (cmApart / pixelsInUnit), 1)


class SliderWithNumber(QWidget):
    valueChanged = Signal(int)

    def __init__(self):
        super().__init__()

        layout = QGridLayout()

        self.slider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(self.onSliderChange)
        layout.addWidget(self.slider, 0, 0)

        self.spinBox = QSpinBox()
        self.spinBox.setMinimumWidth(50)
        self.spinBox.valueChanged.connect(self.onSpinBoxChange)
        layout.addWidget(self.spinBox, 0, 1)

        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def onSliderChange(self):
        newValue = self.slider.value()
        self.spinBox.setValue(newValue)

    def onSpinBoxChange(self):
        newValue = self.spinBox.value()
        # On macOS, the slider doesn't get updated from the
        # spin box after the slider was dragged once
        self.slider.setValue(newValue)
        self.valueChanged.emit(newValue)

    def setValue(self, newValue):
        self.slider.setValue(newValue)
        self.spinBox.setValue(newValue)

    def setMaximum(self, newValue):
        self.slider.setMaximum(newValue)
        self.spinBox.setMaximum(newValue)


class HSVMaskParametersWidget(QWidget):
    valueChanged = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # Config is passed by reference so
        # we can update it from straight from this widget
        self.config: HSVMaskConfigType = parent.config

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Mirror video checkbox
        mirrorLabel = QLabel("Mirror video horizontally")
        layout.addWidget(mirrorLabel)
        mirrorButton = QPushButton("Mirror")
        mirrorButton.setCheckable(True)
        mirrorButton.setChecked(self.config["mirror"])
        mirrorButton.clicked.connect(
            lambda: self.updateMirrorState(mirrorButton.isChecked())
        )
        layout.addWidget(mirrorButton)

        # Spinboxes for each index in crop
        cropLabel = QLabel("Crop")
        layout.addWidget(cropLabel)

        for i, label in enumerate(["y1", "y2", "x1", "x2"]):
            spinBox = QSpinBox()
            spinBox.setRange(0, 2000)
            spinBox.setValue(self.config["crop"][i])
            spinBox.valueChanged.connect(
                # i=i is needed because otherwise i will be the last value
                # (python lambda/passing by reference things)
                lambda x, i=i: self.updateCropState(i, x)
            )
            layout.addWidget(spinBox)

        # Spinbox for cropXUpperBound
        cropXUpperBoundLabel = QLabel("Crop X Upper Bound")
        layout.addWidget(cropXUpperBoundLabel)

        cropXUpperBoundSpinBox = QSpinBox()
        cropXUpperBoundSpinBox.setRange(0, 2000)
        cropXUpperBoundSpinBox.setValue(self.config["cropXUpperBound"])
        cropXUpperBoundSpinBox.valueChanged.connect(
            lambda x: self.updateCropXUpperBoundState(x)
        )

        layout.addWidget(cropXUpperBoundSpinBox)

        # SliderWithNumber widgets for H min-max, S min-max, V min-max
        hsvLabel = QLabel("HSV")
        layout.addWidget(hsvLabel)

        for i, chooseHsv in enumerate(["h", "s", "v"]):
            configToEdit = self.config[chooseHsv]
            hsvSliderLabel = QLabel(chooseHsv)
            layout.addWidget(hsvSliderLabel)

            slider = QLabeledDoubleRangeSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 1)
            slider.setValue([configToEdit[0], configToEdit[1]])
            slider.valueChanged.connect(
                lambda newValue, chooseHsv=chooseHsv: self.updateHSVState(
                    chooseHsv, [newValue[0], newValue[1]]
                )
            )
            layout.addWidget(slider)

        # Width between markers
        widthBetweenMarkersLabel = QLabel("Width between markers in video (px)")
        layout.addWidget(widthBetweenMarkersLabel)

        self.widthBetweenMarkersInput = QLineEdit()
        self.widthBetweenMarkersInput.setText(str(self.config["pixelsInUnit"]))
        self.widthBetweenMarkersInput.textChanged.connect(self.handleWidthBetweenMarkersInput)
        self.widthBetweenMarkersInput.editingFinished.connect(self.displayWidthBetweenMarkersCalculated)
        layout.addWidget(self.widthBetweenMarkersInput)

        # Spin box to set cmApart
        cmApartLabel = QLabel("Width between markers in real life (cm)")
        layout.addWidget(cmApartLabel)

        self.cmApartSpinBox = QDoubleSpinBox()
        self.cmApartSpinBox.setRange(0, 30)
        self.cmApartSpinBox.setSingleStep(0.1)
        self.cmApartSpinBox.setValue(self.config["cmApart"])
        self.cmApartSpinBox.valueChanged.connect(
            lambda x: self.updateConversionState("cmApart", x)
        )
        layout.addWidget(self.cmApartSpinBox)

        self.estimatedPlateLength = -1
        self.plateLengthLabel = QLabel()
        self.plateLengthLabel.setWordWrap(True)
        layout.addWidget(self.plateLengthLabel)

        # Button that prints the config state to the terminal
        debugButton = QPushButton("DEBUG: Print config state")
        debugButton.clicked.connect(self.printConfigState)
        layout.addWidget(debugButton)

        # Add stretch so everything stays on top
        layout.addStretch()

        self.runSettingsChangeCallback()

        self.setLayout(layout)

    def handleWidthBetweenMarkersInput(self, expression: str):
        try:
            x = S(expression)

            # Make sure answer is a integer
            x = int(x)

            self.updateConversionState("pixelsInUnit", x)
        except:
            # an error occurred while parsing the expression
            pass

    def displayWidthBetweenMarkersCalculated(self):
            self.widthBetweenMarkersInput.setText(str(self.config["pixelsInUnit"]))

    def runSettingsChangeCallback(self):
        # Re-calculate the estimated plate length
        self.estimatedPlateLength = calculatePlateWidth(
            self.config["crop"][3] - self.config["crop"][2],
            self.config["cmApart"],
            self.config["pixelsInUnit"],
        )
        self.plateLengthLabel.setText(
            f"Based off the current crop area, the estimated width of the plate will be {self.estimatedPlateLength} cm according to the conversion constants given."
        )

        # Emit valueChanged signal to update annotations
        self.valueChanged.emit()

    def updateHSVState(self, chooseHsv: str, newValue: List[float]):
        self.config[chooseHsv] = newValue
        self.runSettingsChangeCallback()

    def updateCropState(self, cropIdx: int, newValue: int):
        self.config["crop"][cropIdx] = newValue
        self.runSettingsChangeCallback()

    def updateCropXUpperBoundState(self, newValue: int):
        self.config["cropXUpperBound"] = newValue
        self.runSettingsChangeCallback()

    def updateConversionState(self, key: str, newValue):
        self.config[key] = newValue
        self.runSettingsChangeCallback()

    def updateMirrorState(self, newValue: bool):
        self.config["mirror"] = newValue
        self.runSettingsChangeCallback()

    def printConfigState(self):
        print(self.config)
