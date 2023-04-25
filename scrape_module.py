import os
import requests
import shutil
from shutil import copy2
from PIL import Image
from dotenv import load_dotenv  # Add this import

load_dotenv()  # Add this line to load the environment variables

BING_SEARCH_API_KEY = os.getenv('BING_SEARCH_API_KEY')

class ImageDownloader:

    def __init__(self, search_query, num_images_to_download=10, verify=True, license_filter='ModifyCommercially', bing_search_url="https://api.bing.microsoft.com/v7.0/images/search", api_key=BING_SEARCH_API_KEY):
        self.search_query = search_query
        self.num_images_to_download = num_images_to_download
        self.verify = verify
        self.license_filter = license_filter
        self.bing_search_url = bing_search_url
        self.api_key = api_key

        self.image_urls = []
        self.image_files = []

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

    def verify_images(self):
        self.image_files = [f for f in os.listdir('./photos') if f.endswith('.jpg')]
        self.current_index = 0

        while self.current_index < len(self.image_files):
            image_file = f'./photos/{self.current_index + 1}.jpg'
            img = Image.open(image_file)
            img.thumbnail((800, 800))
            img.show()

            response = input('Keep this image? (y/n): ').lower()

            if response == 'y':
                src = f'./photos/{self.current_index + 1}.jpg'
                dest = './verified_photos/'
                if not os.path.exists(dest):
                    os.makedirs(dest)
                copy2(src, dest)
                self.current_index += 1
            elif response == 'n':
                self.current_index += 1
            else:
                print('Invalid input. Please enter y or n.')

    def run(self):
        self.get_bing_image_urls()
        self.save_images()

        if self.verify:
            self.verify_images()
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
    downloader = ImageDownloader("judit polgar", num_images_to_download=20, verify=True)
    downloader.run()
