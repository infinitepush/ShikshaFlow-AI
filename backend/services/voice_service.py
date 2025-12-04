from gtts import gTTS
import os

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
    Simple concatenation approach for MP3 files.
    """
    if not audio_paths:
        raise ValueError("No audio paths provided")
    
    with open(output_path, 'wb') as output_file:
        for i, path in enumerate(audio_paths):
            if not os.path.exists(path):
                raise FileNotFoundError(f"Audio file not found: {path}")
            
            with open(path, 'rb') as input_file:
                data = input_file.read()
                # For MP3 files, we can simply concatenate them
                # This works for files with the same encoding and sample rate
                output_file.write(data)
    
    return output_path