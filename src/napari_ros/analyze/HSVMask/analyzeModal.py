import time
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QDialog, QWidget, QLabel, QGridLayout
from .HSVMaskAnalyzer import HSVMaskAnalyzer
from napari.qt.threading import thread_worker
from pims import ImageSequence

# Should produce the same results re-initializing the analyzer
# here
# TODO: Find a better way to do this
analyzer = HSVMaskAnalyzer()


@thread_worker
def analyzeImageSequence():
    status = "invalid arguments"
    arguments = {}

    while True:
        arguments = yield status
        # check if arguments have a config and imageSequenceDirectory key
        try:
            if "config" in arguments and "imageSequenceDirectory" in arguments:
                config = arguments["config"]
                imageSequenceDirectory = arguments["imageSequenceDirectory"]
                break
        except:
            continue

    status = "reading image sequence"
    yield status

    images = ImageSequence(imageSequenceDirectory)

    # The index for this list is the frame number
    highestXPos = []

    for image in images:
        (
            frame,
            mask,
            highestXPosForThisFrame,
        ) = analyzer.completelyAnalyzeFrame(
            image,
            config["crop"],
            config["mirror"],
            config["h"],
            config["s"],
            config["v"],
            config["areaFilter"],
        )

        highestXPos.append(highestXPosForThisFrame)
        status = f"analyzing frame {len(highestXPos)}"
        yield status

    # Export text file with highestXPos,
    # one value per line
    status = "exporting raw data"
    yield status

    with open(f"{imageSequenceDirectory}/highestXPos.txt", "w") as f:
        for value in highestXPos:
            f.write(f"{value}\n")

    return


class AnalyzeModal(QDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.config = parent.config
        self.imageSequenceDirectory = parent.imageSequenceDirectory

        self.setWindowTitle("Analyzing...")

        layout = QGridLayout()

        # Create a label to display the status
        self.statusLabel = QLabel("starting")
        self.statusLabel.setWordWrap(True)

        # Make the window a bit bigger
        self.resize(400, 100)

        layout.addWidget(self.statusLabel)
        self.setLayout(layout)

        # Initialize the worker
        self.worker = analyzeImageSequence()
        self.worker.yielded.connect(self.on_yielded)
        self.worker.returned.connect(self.on_return)
        self.worker.start()

        # Start the analysis after a short delay
        QTimer.singleShot(1000, self.start_analysis)

    def start_analysis(self):
        self.send_next_value(self.config, self.imageSequenceDirectory)

    def on_yielded(self, value):
        self.statusLabel.setText(value)

    def on_return(self):
        self.statusLabel.setText("done")

    def send_next_value(self, config, imageSequenceDirectory):
        self.worker.send(
            {
                "config": config,
                "imageSequenceDirectory": imageSequenceDirectory,
            }
        )
