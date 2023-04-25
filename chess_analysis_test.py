import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLabel, QPushButton
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class Automator:
    def __init__(self):
        self.browser = None
        self.wait = None

    def open_browser(self):
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 10)
        self.browser.get("https://www.chess.com/analysis")

    def is_browser_open(self):
        return self.browser is not None

    def load_pgn(self, pgn_data):
        pgn_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-cy='pgn-textarea']")))
        pgn_input.clear()
        pgn_input.send_keys(pgn_data)
        pgn_input.send_keys(Keys.RETURN)

    def submit_pgn(self):
        add_games_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cy='add-games-btn']")))
        add_games_button.click()

    def press_back_button(self, delay=0):
        back_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Previous Move']")))
        back_button.click()
        time.sleep(delay)

    def press_forward_button(self, delay=0):
        forward_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next Move']")))
        forward_button.click()
        time.sleep(delay)

    def close_browser(self):
        self.browser.quit()
        
    def change_border_color(self, color):
        self.browser.execute_script(f"document.body.style.border = '5px solid {color}';")

    def login(self):
        login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.icon-font-chess.icon.enter")))
        login_button.click()

        username_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='_username']")))
        username_input.clear()
        username_input.send_keys("Volcanex")

        password_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='_password']")))
        password_input.clear()
        password_input.send_keys("Lasshamster5!")

        login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='login']")))
        login_button.click()
        
    def play_from(self, play_from_data):
        for i in range(play_from_data * 2 - 1):
            time.sleep(0.05)
            self.press_forward_button(delay=0)

    def run_timed(self, timing_data):
        # Navigate the moves using the timing data
        for delay in timing_data:
            self.press_forward_button(self.browser, delay)

    def refresh_chess(self):
        self.browser.get("https://www.chess.com/analysis")

    def run(self, selected_game, login=True):
        
        pgn_data = selected_game["pgn"]
        play_from_data = selected_game["play_from_move"]

        if not self.is_browser_open():
            self.open_browser()

            if login:
                self.login()
                time.sleep(0.5)

        else:
            self.refresh_chess()
        
        self.load_pgn(pgn_data)
        self.submit_pgn()
        time.sleep(0.5)

        self.play_from(play_from_data)

        # Add any other necessary method calls and modifications here
        # ...


class App(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.title = "Select a game or puzzle"
        self.initUI()
        self.automator = Automator()

    def initUI(self):
        self.setWindowTitle(self.title)

        # Create a QVBoxLayout to manage the layout
        layout = QVBoxLayout()

        # Create a QLabel to display instructions
        label = QLabel("Choose a game or puzzle from the dropdown menu and click 'Load':")
        layout.addWidget(label)

        # Create a QComboBox (dropdown menu) to display game titles
        self.combo = QComboBox()
        
        # Sort the data by the "loaded" key in descending order (most recent first)
        self.data.sort(key=lambda x: x['loaded'] or '', reverse=True)
        
        for game in self.data:
            loaded_status = game["loaded"] if game["loaded"] else "NL"
            self.combo.addItem(loaded_status + " - " + game["title"])
            
        layout.addWidget(self.combo)

        # Create a QPushButton to load the selected game
        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_game)
        layout.addWidget(load_button)

        # Set the layout
        self.setLayout(layout)

    def load_game(self):
        selected_game = self.data[self.combo.currentIndex()]
        selected_game["loaded"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open("PGN_TIME_Data.json", "w") as f:
            json.dump(self.data, f, indent=2)

        self.automator.run(selected_game, True)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Load data from the JSON file
    with open("PGN_TIME_Data.json", "r") as f:
        data = json.load(f)

    # Create and display the interface
    interface = App(data)
    interface.show()

    sys.exit(app.exec_())
