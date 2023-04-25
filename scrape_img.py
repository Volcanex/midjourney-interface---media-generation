import os
import requests
import shutil
from shutil import copy2
import tkinter as tk
from PIL import Image, ImageTk
from dotenv import load_dotenv  # Add this import

load_dotenv()  # Add this line to load the environment variables

BING_SEARCH_API_KEY = os.getenv('BING_SEARCH_API_KEY')

def get_bing_image_urls(api_key, search_query, count, bing_search_url, license_filter=None):
    headers = {"Ocp-Apim-Subscription-Key": api_key} 
    params = {
        "q": search_query,
        "count": count,
        "offset": 0,
        "mkt": "en-US",
        "safeSearch": "Moderate",
    }

    if license_filter:
        params["license"] = license_filter

    response = requests.get(bing_search_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    print(data)  # Add this line to print the data

    image_urls = [img['contentUrl'] for img in data['value']]
    return image_urls


def save_images(image_urls, folder_path='./photos/'):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    for i, url in enumerate(image_urls):
        response = requests.get(url, stream=True, headers=headers)
        file_name = f'{folder_path}{i+1}.jpg'

        if response.status_code == 200:
            with open(file_name, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            print(f'Saved image {i+1}: {file_name}')
        else:
            print(f'Error downloading image {i+1}: {url}, status code {response.status_code}')

bing_search_url = BING_SEARCH_API_KEY
api_key = '832e661ae85546899b89544a1d7d3434'  # Replace with your Bing Image Search API key


def run_verify(folder_path='./photos/'):

    def move_image_to_verified(src, dest):
        if not os.path.exists(dest):
            os.makedirs(dest)
        copy2(src, dest)

    def show_image(index):
        global photo
        image_file = f'./photos/{index + 1}.jpg'
        img = Image.open(image_file)
        img.thumbnail((800, 800))
        photo = ImageTk.PhotoImage(img)
        label.config(image=photo)
        label.image = photo
        label_text.config(text=f'Image {index + 1}')

    def next_image():
        nonlocal current_index
        current_index += 1
        if current_index < len(image_files):
            show_image(current_index)
        else:
            root.destroy()

    def keep_image():
        src = f'./photos/{current_index + 1}.jpg'
        dest = './verified_photos/'
        move_image_to_verified(src, dest)
        next_image()

    def delete_image():
        next_image()

    image_files = [f for f in os.listdir('./photos') if f.endswith('.jpg')]
    current_index = 0

    root = tk.Tk()
    root.title('Image Verification')
    root.bind('<Return>', lambda event: keep_image())
    root.bind('<BackSpace>', lambda event: delete_image())

    label = tk.Label(root)
    label.pack()

    label_text = tk.Label(root)
    label_text.pack()

    show_image(current_index)

    button_keep = tk.Button(root, text="Keep", command=keep_image, width=20, height=3)
    button_keep.pack(side='left', padx=10, pady=10)

    button_delete = tk.Button(root, text="Delete", command=delete_image, width=20, height=3)
    button_delete.pack(side='right', padx=10, pady=10)

    root.mainloop()
    
def run(search_query, num_images_to_download=10, verify=True, license_filter='ModifyCommercially', bing_search_url=bing_search_url, api_key=api_key):
    image_urls = get_bing_image_urls(api_key, search_query, num_images_to_download, bing_search_url, license_filter)
    save_images(image_urls)

    
    if verify:
        run_verify()

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



run("judit polgar", 20)
