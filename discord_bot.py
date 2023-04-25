import discord
import threading
import aiohttp
from discord.ext import commands
import os
import requests
from io import BytesIO
from discord import Intents
from midjourney_slicer import slice_image
import asyncio
from dotenv import load_dotenv  # Add this import

load_dotenv()  # Add this line to load the environment variables

TOKEN = os.getenv('DISCORD_TOKEN')  # Update this line
IMG_GEN_BOT_ID = int(os.getenv('IMG_GEN_BOT_ID'))  # Update this line
TEXT_CHANNEL_NAME = os.getenv('TEXT_CHANNEL_NAME')  # Update this line

class ImageBot(commands.Bot):
    def __init__(self):
        intents = Intents.default()
        intents.message_content = True
        intents.messages = True
        self.last_downloaded_image_path = None  # Add this line
        self.image_received = asyncio.Event()
        
        super().__init__(command_prefix='!', intents=intents)

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    async def download_and_rename_image(self, attachment, folder_path, new_name):
        response = requests.get(attachment.url)
        image_data = BytesIO(response.content)

        _, file_extension = os.path.splitext(attachment.filename)
        image_path = os.path.join(folder_path, f"{new_name}{file_extension}")
        
        with open(image_path, 'wb') as f:
            f.write(image_data.getbuffer())

        print(f'Image {new_name} saved at path {image_path}!')

        return image_path

bot = ImageBot()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
    # Find the text channel by its name
    for guild in bot.guilds:
        for channel in guild.channels:
            if channel.name == TEXT_CHANNEL_NAME:
                text_channel = channel
                break
    
    # Send the message to the text channel
    await text_channel.send("Discord bot initilized!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.id == IMG_GEN_BOT_ID:
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    response = requests.get(attachment.url)
                    image_data = BytesIO(response.content)

                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    images_dir = os.path.join(script_dir, 'images')
                    os.makedirs(images_dir, exist_ok=True)

                    image_path = os.path.join(images_dir, attachment.filename)
                    with open(image_path, 'wb') as f:
                        f.write(image_data.getbuffer())

                    bot.last_downloaded_image_path = image_path  # Update the last_downloaded_image_path attribute
                    print("Setting the image_received event")
                    bot.image_received.set()
                    
                    # Slice the image and save the four halves
                    slice_image(image_path)

                    print(f'Image {attachment.filename} saved at path {image_path} and sliced!')

    await bot.process_commands(message)

def run_bot_in_thread():
    def run_bot():
        bot.run(TOKEN)

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    return bot_thread

if __name__ == '__main__':
    bot.run(TOKEN)
