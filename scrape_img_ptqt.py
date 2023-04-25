import os
import requests
import shutil
from shutil import copy2
from PIL import Image, ImageTk
from PyQt5 import QtWidgets, QtGui, QtCore
from dotenv import load_dotenv  # Add this import

load_dotenv()  # Add this line to load the environment variables


BING_SEARCH_API_KEY = os.getenv('BING_SEARCH_API_KEY')

class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.bing_search_url = "https://api.bing.microsoft.com/v7.0/images/search"
        self.api_key = BING_SEARCH_API_KEY # Replace with your Bing Image Search API key

        self.search_query = "judit polgar"
        self.num_images_to_download = 10
        self.verify = True
        self.license_filter = 'ModifyCommercially'
        
        self.image_urls = []
        self.image_files = []

        self.setup_ui()
        self.run()

    def setup_ui(self):
        self.setWindowTitle('Image Verification')
        self.setGeometry(50, 50, 800, 450)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)

        self.image_text_label = QtWidgets.QLabel()
        self.image_text_label.setAlignment(QtCore.Qt.AlignCenter)

        self.keep_button = QtWidgets.QPushButton('Keep')
        self.keep_button.clicked.connect(self.keep_image)
        self.delete_button = QtWidgets.QPushButton('Delete')
        self.delete_button.clicked.connect(self.delete_image)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.keep_button)
        button_layout.addWidget(self.delete_button)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addWidget(self.image_text_label)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def get_bing_image_urls(self):
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {
            "q": self.search_query,
            "count": self.num_images_to_download,
            "offset": 0,
            "mkt": "en-US",
            "safeSearch": "Moderate",
        }

        if self.license_filter:
            params["license"] = self.license_filter

        response = requests.get(self.bing_search_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        print(data)  # Add this line to print the data

        self.image_urls = [img['contentUrl'] for img in data['value']]

    def save_images(self):
        folder_path = './photos/'

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

        for i, url in enumerate(self.image_urls):
            response = requests.get(url, stream=True, headers=headers)
            file_name = f'{folder_path}{i+1}.jpg'

            if response.status_code == 200:
                with open(file_name, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                print(f'Saved image {i+1}: {file_name}')
            else:
                print(f'Error downloading image {i+1}: {url}, status code {response.status_code}')

    def run_verify(self):
        self.image_files = [f for f in os.listdir('./photos') if f.endswith('.jpg')]
        self.current_index = 0

        self.show_image(self.current_index)

        self.show()

    def show_image(self, index):
        image_file = f'./photos/{index + 1}.jpg'
        pixmap = QtGui.QPixmap(image_file)
        scaled_pixmap = pixmap.scaled(self.image_label.size(), QtCore.Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)

        self.image_text_label.setText(f'Image {index + 1}')

    def next_image(self):
        self.current_index += 1
        if self.current_index < len(self.image_files):
            self.show_image(self.current_index)
        else:
            self.close()

    def keep_image(self):
        src = f'./photos/{self.current_index + 1}.jpg'
        dest = './verified_photos/'
        if not os.path.exists(dest):
            os.makedirs(dest)
        copy2(src, dest)
        self.next_image()

    def delete_image(self):
        self.next_image()

    def run(self):
        self.get_bing_image_urls()
        self.save_images()

        if self.verify:
            self.run_verify()
        else:
            src_folder = './photos/'
            dest_folder = './verified_photos/'

            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            for file_name in os.listdir(src_folder):
                if file_name.endswith('.jpg'):
                    src = os.path.join(src_folder, file_name)
                    dest = os.path.join(dest_folder, file_name)
                    shutil.move(src, dest)
                    print(f'Moved {file_name} to verified_photos folder.')


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    main_window = MainWindow()
    app.exec_()
