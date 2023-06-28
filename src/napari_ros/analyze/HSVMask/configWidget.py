from qtpy.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


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

        self.config = parent.config

        layout = QVBoxLayout()

        # Add label for now
        label = QLabel("HSVMaskConfigWidget")

        layout.addWidget(label)

        self.setLayout(layout)
