import time
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QDialog, QWidget, QLabel, QGridLayout
from .HSVMaskAnalyzer import HSVMaskAnalyzer
from napari.qt.threading import thread_worker
from pims import ImageSequence
import os

# Should produce the same results re-initializing the analyzer
# here
# TODO: Find a better way to do this
analyzer = HSVMaskAnalyzer()

from .postProcess import postProcess


@thread_worker
def analyzeImageSequence():
    status = "checking arguments..."
    arguments = {}

    while True:
        arguments = yield status
        # check if arguments have a config and imageSequenceDirectory key
        try:
            if "config" in arguments and "imageSequenceDirectory" in arguments and "title" in arguments:
                config = arguments["config"]
                imageSequenceDirectory = arguments["imageSequenceDirectory"]
                title = arguments["title"]
                break
        except:
            continue

    # Make directory ../data/config["title"] (starting from imageSequenceDirectory)
    dataExportDir = os.path.join(imageSequenceDirectory, os.pardir, "data", title)
    os.makedirs(dataExportDir, exist_ok=True)

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
        )

        highestXPos.append(highestXPosForThisFrame)
        status = f"analyzing frame {len(highestXPos)}"
        yield status

    status = "post processing data"
    yield status

    postProcess(highestXPos, config, arguments["title"], dataExportDir)

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
        # title should be the name of the directory only 
        titleOfPostProcess = os.path.basename(imageSequenceDirectory)
        self.worker.send(
            {
                "config": config,
                "imageSequenceDirectory": imageSequenceDirectory,
                "title": titleOfPostProcess
            }
        )
