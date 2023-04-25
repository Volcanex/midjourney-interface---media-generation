import os
import time
import asyncio
from discord_bot_prompting import DiscordBotPrompter
from discord_bot import ImageBot, bot, slice_image
import requests
from io import BytesIO
import functools
from text_to_speech import synthesize_speech, save_speech_to_file
from transcribe_audio import AutomaticSubtitles
from midjourney_slicer import slice_image_alt  # Add this import
import asyncio
from discord_bot import bot, run_bot_in_thread
import json
from dotenv import load_dotenv  # Add this import

load_dotenv()  # Add this line to load the environment variables

DISCORD_EMAIL = os.getenv('DISCORD_EMAIL')  # Update this line
DISCORD_PASSWORD = os.getenv('DISCORD_PASSWORD')  # Update this line
DISCORD_CHANNEL_LINK = os.getenv('DISCORD_CHANNEL_LINK')  # Update this line

class FileGenerator:
    def __init__(self, resources):
        self.resources = resources
        self.file_paths = {}
        self.bot_thread = run_bot_in_thread()  # Add this line
        self.prompter = DiscordBotPrompter(DISCORD_EMAIL,DISCORD_PASSWORD,DISCORD_CHANNEL_LINK)

    def generate_files(self):
        for resource in self.resources:
            resource_id = resource['id']
            resource_type = resource['type']
            resource_content = resource['content']

            # Create a folder for each resource type if it doesn't exist
            folder_path = os.path.join('_tools', resource_type)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            print(f"Generating {resource_type} file for resource ID {resource_id}...")

            # Call the appropriate method to generate the file
            if resource_type == 'image':
                current_loop = asyncio.get_event_loop()
                file_path = current_loop.run_until_complete(self.generate_image(resource_content, folder_path))

            elif resource_type == 'voice':  # Change 'audio' to 'voice'
                file_path = self.generate_voice(resource_content, folder_path)

            elif resource_type == 'subtitle':
                # Use the GPT-generated text as the content for the subtitles
                gpt_generated_text = self.prompter.get_generated_text()
                file_path = self.generate_subtitle(gpt_generated_text, folder_path)
            else:
                raise ValueError(f'Unsupported resource type: {resource_type}')

            # Save the generated file path with its ID
            self.file_paths[str(resource_id)] = file_path

            print(f"Generated {resource_type} file for resource ID {resource_id} at path {file_path}")

    async def on_message(self, message, folder_path, prompter):
        if message.author == bot.user:
            return

        if message.author.id == 936929561302675456:  # Replace with your ImageGenBot ID
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        time.sleep(20)  # Wait for 20 seconds to see if the image is available for download
                        image_path = os.path.join(folder_path, attachment.filename)

                        if not os.path.exists(image_path):
                            prompter.click_button(416, 632)  # Click the upscale button
                            time.sleep(3)  # Wait for the upscaled image to load

                        await self.download_and_save_image(attachment, folder_path)
                        slice_image_alt(image_path)  # Call the slice_image_alt function instead
                        print(f"Sliced image file at path {image_path}")
                        break

    async def generate_image(self, content, folder_path):
        prompt = f" {content}"
        print(f"Generating image file for content: {content}...")

        self.prompter.type_message("/imagine")
        time.sleep(1)
        self.prompter.type_message(prompt)
        self.prompter.send_message()

        print("Waiting for ImageGenBot to generate and send the image...")

        try:
            await asyncio.wait_for(bot.image_received.wait(), timeout=80)  # Wait for the image_received event
            bot.image_received.clear()  # Clear the event after it has been set

            image_path = bot.last_downloaded_image_path
            if image_path:
                slice_image_alt(image_path)
                print(f"Sliced image file at path {image_path}")
            else:
                print("Failed to get the image from the ImageGenBot.")
        except asyncio.TimeoutError:
            print("Timeout while waiting for the image from the ImageGenBot.")
            image_path = None
            TimeoutError()

        return image_path


    def generate_voice(self, text, folder_path):
  # Change the method signature
        filename = f"{text[:15]}.mp3"
        file_path = os.path.join(folder_path, filename)  # Create an output file name based on the text
        print(f"Generating audio file for text: {text}...")
        audio_content = synthesize_speech(text)
        save_speech_to_file(audio_content, file_path)
        return file_path

    def get_file_paths(self):
        return self.file_paths

    def save_file_paths(self):
        with open("existing_resources.json", "w") as file:
            json.dump(self.file_paths, file, indent=4)
            print("File paths saved to existing_resources.json")

