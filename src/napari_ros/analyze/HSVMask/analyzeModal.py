from qtpy.QtWidgets import QDialog, QWidget


class AnalyzeModal(QDialog):
    def __init__(self, parent: QWidget):
        super().__init__()

        # Show text for now
        self.setWindowTitle("Analyzing...")
