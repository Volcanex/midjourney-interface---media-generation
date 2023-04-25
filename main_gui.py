import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QProgressBar, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from main import run_main
import threading



class MainWindow(QMainWindow):
    messages_to_progress = {
        "Reading video.json file...": 5,
        "Generating files...": 10,
        "Retrieving file paths of generated resources...": 75,
        "Initializing resources for video editor...": 80,
        "Creating final video...": 85,
        "Final video created.": 100,
    }
    
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_process)
        layout.addWidget(self.start_button)

        self.progress_label_1 = QLabel('Progress')
        layout.addWidget(self.progress_label_1)
        self.progress_bar_1 = QProgressBar()
        layout.addWidget(self.progress_bar_1)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.log_view)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def start_process(self):
        main_thread = threading.Thread(target=run_main, args=(self.update_gui,))
        main_thread.start()

    def add_log_message(self, message):
        self.log_view.append(message)

    def update_gui(self, message):
        self.add_log_message(message)
        progress_value = self.messages_to_progress.get(message)
        if progress_value is not None:
            self.progress_bar_1.setValue(progress_value)

        # USING MESSAGES TO UPDATE BARS, INACCURATE

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
