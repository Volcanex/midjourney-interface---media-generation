import json
from file_generator import FileGenerator
from video_editor import VideoEditor
from resource_handler import ResourceHandler
import os

# Set the working directory to the location of this script
script_dir = os.path.dirname(os.path.realpath(__file__))
print(f"Setting working directory to {script_dir}")
os.chdir(script_dir)

def read_video_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    print(f"Reading video.json file from {file_path}")
    return data

def run_main(skip_resource_generation=False, update_callback=None):
    # Read the video.json file
    print("Reading video.json file...")
    if update_callback:
        update_callback("Reading video.json file...")
    video_data = read_video_json('video.json')

    if not skip_resource_generation:
        # Generate the files based on the content in the resources section
        print("Generating files...")
        if update_callback:
            update_callback("Generating files...")
        file_generator = FileGenerator(video_data['resources'])
        file_generator.generate_files()

        # Get the file paths of the generated resources
        print("Retrieving file paths of generated resources...")
        if update_callback:
            update_callback("Retrieving file paths of generated resources...")
        file_paths = file_generator.get_file_paths()

        # Save the file paths of the generated resources
        file_generator.save_file_paths()

    else:
        # Load existing resources from a JSON file
        with open("existing_resources.json", "r") as file:
            file_paths = json.load(file)
    
    print(f"File paths: {file_paths}")

    # Initialize the resources for the video editor
    print("Initializing resources for video editor...")
    if update_callback:
        update_callback("Initializing resources for video editor...")

    resource_handler = ResourceHandler(file_paths)
    resources = resource_handler.initialize_resources()

    # Create the final video using the VideoEditor class
    print("Creating final video...")
    if update_callback:
        update_callback("Creating final video...")
        
    video_editor = VideoEditor(video_data['channels'], resources)
    video_editor.create_video()


if __name__ == '__main__':
    run_main(skip_resource_generation=False)