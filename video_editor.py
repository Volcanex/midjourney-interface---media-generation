from moviepy.editor import concatenate_videoclips, ImageClip, CompositeVideoClip, AudioFileClip, concatenate_audioclips
from resource_handler import ResourceHandler
import os
from moviepy.audio.AudioClip import AudioArrayClip

import numpy as np

class VideoEditor:
    def __init__(self, channels, resources):
        self.channels = channels
        self.resources = resources
        self.audio_clips = []

    def create_video(self):
        video_clips = []
        audio_clips = []

        for channel in self.channels:
            channel_name = channel['name']
            channel_type = channel['type']
            channel_content = channel['content']

            if channel_type == 'image':
                for content_item in channel_content:
                    start_time = content_item['start_time']
                    end_time = content_item['end_time']
                    file_id = content_item['file_id']
                    file_path = self.resources[file_id]
                    video_clip = self.add_resource_to_video(file_path, start_time, end_time)
                    video_clips.append(video_clip)

            elif channel_type == 'audio':
                channel_audio_clips = self.add_audio_clips(channel_content, self.resources)  # Call the add_audio_clips method
                audio_clips.extend(channel_audio_clips)
                    
        if not video_clips:  # Check for an empty video_clips list
            print("No video clips were generated.")
            return

        final_video = concatenate_videoclips(video_clips)

        if not audio_clips:
            print("No audio clips were generated.")
            silence = AudioArrayClip(np.zeros((int(final_video.duration * 44100), 2), dtype="int16"), fps=44100)
            audio_clips.append(silence)

        final_audio = concatenate_audioclips(audio_clips)
        silence_duration = final_video.duration - final_audio.duration

        if silence_duration > 0:
            silence = AudioArrayClip(np.zeros((int(silence_duration * 44100), 2), dtype="int16"), fps=44100)  # Generate silence
            final_audio = concatenate_audioclips([final_audio, silence])  # Add silence to the end

        final_video = final_video.set_audio(final_audio)

        print("Video and audio clips concatenated successfully!")

        os.makedirs("generated_videos", exist_ok=True)
        output_path = os.path.join("generated_videos", "final_video.mp4")

        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

        print(f"Final video saved at path: {output_path}")



    def add_resource_to_video(self, file_path, start_time, end_time):
        duration = end_time - start_time
        image_clip = ImageClip(file_path, duration=duration)
        print(f"Image clip added to video from file: {file_path}")
        return image_clip


    def add_audio_clips(self, channel_content, resources):
        audio_clips = []
        for index, item in enumerate(channel_content):
            resource_id, start_time, end_time = item['file_id'], item['start_time'], item['end_time']
            resource = resources[str(resource_id)]
            audio_clip = AudioFileClip(resource)

            # Ensure start_time and end_time are within the clip's duration
            start_time = min(start_time, audio_clip.duration)
            end_time = min(end_time, audio_clip.duration)

            # Cut the audio clip to the specified duration
            audio_clip = audio_clip.subclip(start_time, end_time)

            audio_clips.append(audio_clip)

        return audio_clips



