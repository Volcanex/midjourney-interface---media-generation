from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.chrome.options import Options

class DiscordBotPrompter:
    def __init__(self, email, password, guild_url):
        self.email = email
        self.password = password
        self.guild_url = guild_url

        # Create Chrome options
        chrome_options = Options()
        
        # Set the initial window size to the smallest possible dimensions
        chrome_options.add_argument("--window-size=1,1")
        
        # Set the initial window position
        chrome_options.add_argument(f"--window-position=1,155")

        # Create the webdriver with the specified options
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)

        self.login()

    def resize_window(self, width, height):
        self.driver.set_window_size(width, height)

    def reposition_window(self, x, y):
        self.driver.set_window_position(x, y)

    def login(self):
        print("Logging in...")
        
        # Use webdriver.Firefox() if you prefer Firefox
        self.driver.get(self.guild_url)
        print("Loaded webdriver?")
        time.sleep(3)

        email_input = self.driver.find_element(By.NAME, "email")
        email_input.send_keys(self.email)
        print("Entered email")

        password_input = self.driver.find_element(By.NAME, "password")
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        print("Entered password")

        time.sleep(5)

        # Wait for the client to load and send a message
        self.resize_window(1024, 768)  # Resize the window to the desired dimensions
        self.reposition_window(1, 1)
        time.sleep(1)
        self.type_message("Prompt entry ready to go!")
        self.send_message()

    def click_button(self, x, y):
        try:
            # Click the button using x and y coordinates
            ActionChains(self.driver).move_by_offset(x, y).click().perform()
            ActionChains(self.driver).move_by_offset(-x, -y).perform()  # Reset mouse position
            print(f"Clicked button at ({x}, {y})")

        except Exception as e:
            print(f"Error clicking button: {e}")

    def click_message_box(self):
        try:
            # Click the text box using x and y coordinates
            ActionChains(self.driver).move_by_offset(510, 740).click().perform()
            ActionChains(self.driver).move_by_offset(-510, -740).perform()  # Reset mouse position
            print("Clicked text box")

        except Exception as e:
            print(f"Error typing message: {e}")

    def type_message(self, message):
        try:


            # Type the message
            actions = ActionChains(self.driver)
            actions.send_keys(message)
            actions.perform()
            print(f"Typed message: {message}")

        except Exception as e:
            print(f"Error typing message: {e}")

    def send_message(self):
        try:
            # Press enter to send the message
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.ENTER)
            actions.perform()
            print("Sent message")

        except Exception as e:
            print(f"Error sending message: {e}")


    def close(self):
        self.type_message("Offline! [Prompt-Entry]")
        self.driver.quit()
        print("Closed the driver")
