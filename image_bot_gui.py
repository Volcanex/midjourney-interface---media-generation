import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
import discord_bot
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QWidget, QLineEdit, QLabel,
    QCheckBox, QComboBox, QSlider, QSpinBox
)
import asyncio
from discord_bot_prompting import DiscordBotPrompter
import time 
import os 
import json
import os.path
from PyQt5.QtCore import QThread
from loading_window import LoadingWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog
import csv
from dotenv import load_dotenv  # Add this import

load_dotenv()  # Add this line to load the environment variables

DISCORD_EMAIL = os.getenv('DISCORD_EMAIL')  # Update this line
DISCORD_PASSWORD = os.getenv('DISCORD_PASSWORD')  # Update this line
DISCORD_CHANNEL_LINK = os.getenv('DISCORD_CHANNEL_LINK')  # Update this line

class BotWorker(QObject):
    start_bot_signal = pyqtSignal()

    @pyqtSlot()
    def run_bot(self):
        discord_bot.bot.run(discord_bot.TOKEN)

class PrompterWorker(QObject):
    initialized = pyqtSignal()

    @pyqtSlot()
    def init_prompter(self):
        self.discord_bot_prompter = DiscordBotPrompter(DISCORD_EMAIL, DISCORD_PASSWORD, DISCORD_CHANNEL_LINK)
        self.initialized.emit()

class ImageBotGui(QMainWindow):
    def __init__(self):
        super().__init__()

        self.combos = {}

        # Show the loading window
        self.loading_window = LoadingWindow()
        self.loading_window.show()

        # Initialize the DiscordBotPrompter in a separate thread
        self.prompter_thread = QThread()
        self.prompter_worker = PrompterWorker()
        self.prompter_worker.moveToThread(self.prompter_thread)
        self.prompter_thread.started.connect(self.prompter_worker.init_prompter)
        self.prompter_worker.initialized.connect(self.on_prompter_initialized)
        self.prompter_thread.start()

    def on_prompter_initialized(self):
        self.discord_bot_prompter = self.prompter_worker.discord_bot_prompter
        self.initUI()
        self.loading_window.close()  # Close the loading window after initializing the Prompter


    def delayed_init(self):
        self.init_prompter()
        self.initUI()

    def init_prompter(self):
        self.discord_bot_prompter = DiscordBotPrompter("gabrielpenman@gmail.com", "Lasshamster5!", "https://discord.com/channels/1094637190094540912/1094637190618808342")
        self.loading_window.close()  # Close the loading window after initializing the Prompter

    def initUI(self):
        self.setWindowTitle('Image Bot')

        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "modifiers.json")

        if not os.path.exists(json_path):
            empty_modifiers = {}

            with open(json_path, "w") as file:
                json.dump(empty_modifiers, file, indent=4)
            print("Modifiers.json created!")

        else:
            print("Modifiers.json found!")

        with open(json_path, "r") as file:
            self.modifiers = json.load(file)

        self.create_elements()

        self.setGeometry(1030, 0, 300, 200)
        self.show()


    def create_elements(self):
        self.layout = QVBoxLayout()

        self.prompt_label = QLabel("Enter your prompt:")
        self.layout.addWidget(self.prompt_label)

        self.prompt_edit = QLineEdit()
        self.layout.addWidget(self.prompt_edit)

        self.clear_entry_checkbox = QCheckBox("Clear entry after sending")
        self.layout.addWidget(self.clear_entry_checkbox)

        # Move the "Send Prompt" button here
        self.send_button = QPushButton("Send Prompt")
        self.send_button.clicked.connect(self.send_manual_prompt)
        self.layout.addWidget(self.send_button)

        self.controls = {}

        for category, value in self.modifiers.items():
            label = QLabel(f"{category}:")
            self.layout.addWidget(label)

            control_type = value["control"]

            if control_type == "dropdown":
                control = QComboBox()
                control.addItem("Default")  # Add the default option
                for item in value["options"]:
                    control.addItem(item)

                self.combos[category] = control  # Update this line to populate self.combos dictionary

            elif control_type == "entry_slider":
                control = QSlider(Qt.Horizontal)
                control.setMinimum(value["min"])
                control.setMaximum(value["max"])
            elif control_type == "entry_dropdown":
                control = QLineEdit()

            self.layout.addWidget(control)
            self.controls[category] = control

        # Add Select Text File and Run Text File buttons
        self.select_text_file_button = QPushButton("Select Text File")
        self.select_text_file_button.clicked.connect(self.select_text_file)
        self.layout.addWidget(self.select_text_file_button)

        # The "Run Text File" button stays at the bottom
        self.run_text_file_button = QPushButton("Run Text File")
        self.run_text_file_button.clicked.connect(self.run_text_file_prompts)
        self.layout.addWidget(self.run_text_file_button)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)


    def select_text_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Text File", "", "Text Files (*.txt)", options=options)
        if file_name:
            self.text_file_path = file_name

    def run_text_file_prompts(self):
        if hasattr(self, 'text_file_path'):
            with open(self.text_file_path, 'r') as textfile:
                for line in textfile:
                    prompt = line.strip()  # Remove leading/trailing whitespaces and newline characters
                    self.send_prompt(prompt)
                    time.sleep(1)  # Add a delay between prompts (optional)
        else:
            print("No text file selected")

    def send_manual_prompt(self):
        self.send_prompt(self.prompt_edit.text())

    def send_prompt(self, prompt_text):

        modifiers = [combo.currentText() for combo in self.combos.values() if combo.currentText() != "Default"]
        parameters = []

        for param_key, param_info in self.modifiers.items():
            if param_info["type"] == "parameter":
                param_widget = self.controls[param_key]
                value = None
                if isinstance(param_widget, QSlider):
                    value = param_widget.value()
                elif isinstance(param_widget, QComboBox):
                    value = param_widget.currentText()
                elif isinstance(param_widget, QLineEdit):
                    value = param_widget.text()

                if value is not None and value != "Default":  # Check if the value is not "Default"
                    param_prefix = param_info["parameter_prefix"]
                    parameters.append(f"{param_prefix} {value}")

        formatted_prompt = f"{prompt_text}, " + ' '.join(modifiers + parameters)
        print("Sending prompt:", formatted_prompt)

        self.discord_bot_prompter.click_message_box()
        self.discord_bot_prompter.type_message("/imagine")
        time.sleep(1)
        self.discord_bot_prompter.click_message_box()
        self.discord_bot_prompter.type_message(" "+formatted_prompt)
        time.sleep(0.3)
        self.discord_bot_prompter.send_message()

        if self.clear_entry_checkbox.isChecked():
            self.prompt_edit.clear()  # Clear the text box




app = QApplication(sys.argv)
gui = ImageBotGui()

bot_thread = QThread()
bot_worker = BotWorker()
bot_worker.moveToThread(bot_thread)
bot_thread.started.connect(bot_worker.run_bot)
bot_worker.start_bot_signal.connect(bot_worker.run_bot)
bot_thread.start()
bot_worker.start_bot_signal.emit()

app.exec_()
