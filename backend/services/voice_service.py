from gtts import gTTS
import os
from moviepy import AudioFileClip, concatenate_audioclips

def generate_voiceover(script_text, path):
    try:
        tts = gTTS(text=script_text, lang='en', slow=False)
        tts.save(path)

        # Verify file was created and is not empty
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            raise RuntimeError(f"gTTS failed to create a valid audio file for path: {path}")

    except Exception as e:
        print(f"Error during gTTS generation for '{path}': {e}")
        # Re-raise the exception to be handled by the controller
        raise e
    
    return path

def combine_audio(audio_paths, output_path):
    """
    Combine multiple audio files into one.
    """
    if not audio_paths:
        raise ValueError("No audio paths provided")

    clips = []
    for path in audio_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Audio file not found: {path}")
        clips.append(AudioFileClip(path))

    try:
        combined = concatenate_audioclips(clips)
        combined.write_audiofile(output_path, logger=None)
        combined.close()
        return output_path
    finally:
        for clip in clips:
            clip.close()
