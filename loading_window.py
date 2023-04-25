from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import QTimeLine, Qt

class LoadingWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Loading")
        self.setGeometry(0, 0, 300, 60)

        layout = QVBoxLayout()
        self.label = QLabel("Loading:")
        layout.addWidget(self.label)

        self.progress = QProgressBar(self)
        layout.addWidget(self.progress)

        self.setLayout(layout)

        # Create a QTimeLine instance with 30,000 milliseconds (30 seconds) duration
        self.timeline = QTimeLine(45000, self)
        self.timeline.setFrameRange(0, 100)
        self.timeline.frameChanged.connect(self.on_frame_changed)
        self.timeline.start()

    def on_frame_changed(self, value):
        self.progress.setValue(value)
