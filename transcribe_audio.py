import os
import io
import glob
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment

# Replace 'heatmap-381816-3975f36b985c.json' with your JSON key file name
json_key_file = 'transcribe_json_key.json'

# Get the absolute path of the JSON key file
json_key_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), json_key_file)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_file_path

class AutomaticSubtitles:
    def __init__(self, json_key_path=json_key_file_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = json_key_path
        self.client = speech.SpeechClient()

    def transcribe_audio(self, audio_file_path, language_code="en-US"):
        # Load audio file
        audio_file = AudioSegment.from_file(audio_file_path, format="wav")

        # Convert audio to mono
        audio_file = audio_file.set_channels(1)

        # Export the audio to a new file
        mono_audio_file_path = os.path.join(mono_folder_path, "mono_" + os.path.basename(audio_file_path))

        audio_file.export(mono_audio_file_path, format="wav")

        file_extension = os.path.splitext(audio_file_path)[1].lower()

        if file_extension == ".mp3":
            audio = AudioSegment.from_mp3(audio_file_path)
            audio_file_path = os.path.splitext(audio_file_path)[0] + ".wav"
            audio.export(audio_file_path, format="wav")

        # Use the mono_audio_file_path instead of audio_file_path
        with io.open(mono_audio_file_path, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            # Remove the sample_rate_hertz parameter, allowing the API to automatically detect it
            language_code=language_code,
            enable_word_time_offsets=True,
        )

        response = self.client.recognize(config=config, audio=audio)
        return response

    def generate_subtitles(self, audio_file_path, language_code="en-US"):
        response = self.transcribe_audio(audio_file_path, language_code)
        subtitles = []

        for result in response.results:
            alternative = result.alternatives[0]
            for word_info in alternative.words:
                word = word_info.word
                start_time = word_info.start_time.total_seconds()
                end_time = word_info.end_time.total_seconds()
                subtitles.append((word, start_time, end_time))

        return subtitles


def create_folders_and_example(to_transcribe_path, transcribed_path):
    os.makedirs(to_transcribe_path, exist_ok=True)
    os.makedirs(transcribed_path, exist_ok=True)

def create_mono_folder(mono_folder_path):
    os.makedirs(mono_folder_path, exist_ok=True)

def convert_mp3_to_wav(mp3_file_path):
    audio = AudioSegment.from_mp3(mp3_file_path)
    wav_file_path = os.path.splitext(mp3_file_path)[0] + ".wav"
    audio.export(wav_file_path, format="wav")
    return wav_file_path

def process_audio_files(to_transcribe_path, transcribed_path):
    subtitle_generator = AutomaticSubtitles(json_key_file_path)

    for audio_file_path in glob.glob(os.path.join(to_transcribe_path, "*.[mM][pP]3")):
        audio_file_path = convert_mp3_to_wav(audio_file_path)

    for audio_file_path in glob.glob(os.path.join(to_transcribe_path, "*.[wW][aA][vV]")):
        print(f"Processing: {audio_file_path}")
        subtitles = subtitle_generator.generate_subtitles(audio_file_path)

        base_filename = os.path.splitext(os.path.basename(audio_file_path))[0]
        srt_file_path = os.path.join(transcribed_path, f"{base_filename}.srt")

        with open(srt_file_path, "w") as srt_file:
            for i, (word, start_time, end_time) in enumerate(subtitles):
                srt_file.write(f"{i+1}\n")
                srt_file.write(f"{start_time:.3f} --> {end_time:.3f}\n")
                srt_file.write(f"{word}\n\n")

        print(f"Finished: {srt_file_path}")

if __name__ == "__main__":

    script_directory = os.path.dirname(os.path.abspath(__file__))
    mono_folder_path = os.path.join(script_directory, 'transcribing_mono')
    
    to_transcribe_path = os.path.join(script_directory, 'to_transcribe')
    transcribed_path = os.path.join(script_directory, 'transcribed')
    create_mono_folder(mono_folder_path)
    create_folders_and_example(to_transcribe_path, transcribed_path)
    process_audio_files(to_transcribe_path, transcribed_path)
