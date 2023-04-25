
import os
import glob
from google.cloud import texttospeech


# Replace 'heatmap-381816-3975f36b985c.json' with your JSON key file name
json_key_file = 'tts_json_key'

# Get the absolute path of the JSON key file
json_key_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), json_key_file)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_file_path


def synthesize_speech(text, language_code='en-US', gender='NEUTRAL'):
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.SsmlVoiceGender[gender]
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=input_text,
        voice=voice,
        audio_config=audio_config
    )

    return response.audio_content

def save_speech_to_file(audio_content, output_file):
    with open(output_file, 'wb') as f:
        f.write(audio_content)

def process_text_files(input_folder, output_folder):
    for text_file in glob.glob(os.path.join(input_folder, '*.txt')):
        with open(text_file, 'r') as f:
            text = f.read()

        audio_content = synthesize_speech(text)
        output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(text_file))[0] + '.mp3')
        save_speech_to_file(audio_content, output_file)

def create_folders_and_example(input_folder, output_folder):
    script_path = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(script_path, input_folder)
    output_folder = os.path.join(script_path, output_folder)

    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        example_text_file = os.path.join(input_folder, 'example.txt')
        with open(example_text_file, 'w') as f:
            f.write("This is an example text file.")
    os.makedirs(output_folder, exist_ok=True)


if __name__ == "__main__":
    input_folder = 'text_files'
    output_folder = 'voice_files'
    
    script_path = os.path.dirname(os.path.abspath(__file__))
    input_folder_path = os.path.join(script_path, input_folder)
    output_folder_path = os.path.join(script_path, output_folder)

    create_folders_and_example(input_folder, output_folder)
    process_text_files(input_folder_path, output_folder_path)

