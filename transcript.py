import whisper
import time
import logging
import json
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def transcribe_audio_with_whisper(audio_file_path, model_size="base"):
    """
    Loads a Whisper model and transcribes an audio file.

    Parameters:
    audio_file_path (str): The path to the audio file to be transcribed.
    model_size (str): The size of the Whisper model to load (default is "base") Available models- small,base,medium,large.

    Returns:
    str: The transcribed text from the audio file.
    """
    try:
        # Measure model load time
        logging.info('Starting transcription process...')
        start_time = time.time()
        logging.info('Loading Whisper model...')
        model = whisper.load_model(model_size)
        end_time = time.time()
        model_load_time = end_time - start_time
        logging.info(f'Model load time: {model_load_time:.2f} seconds')

        # Check if the model load time is unusually long
        if model_load_time > 30:
            logging.warning('Model load time is unusually long.')

        # Measure transcription time
        st = time.time()
        logging.info('Transcribing audio...')
        transcript = model.transcribe(audio_file_path)
        et = time.time()
        transcription_time = et - st
        logging.info(f'Transcription generation time: {transcription_time:.2f} seconds')

        # Check if the transcription time is unusually long
        if transcription_time > 60:
            logging.warning('Transcription time is unusually long.')

        logging.info('Transcription process completed successfully.')
        # Return the transcribed text
        return transcript
    except FileNotFoundError as e:
        logging.error(f'File not found: {audio_file_path}')
    except Exception as e:
        logging.error(f'An error occurred: {e}')

# Example usage
audio_file_path = r"C:\Users\MohammedKareemKhan\Desktop\project\video-to-notes\audio_from video\addition.mp3"
transcribed_text = transcribe_audio_with_whisper(audio_file_path)

if transcribed_text:
    print(f'Transcript Generated from model: {transcribed_text}')
    print(type(transcribed_text))

# Saving the generated transcript as JSON file
transcript_file_path = r'C:\Users\MohammedKareemKhan\Desktop\project\video-to-notes\transcripts\transcript.jsoon'
with open(transcript_file_path,'w') as file:
    json.dump(transcribed_text, file)

print(f'transcript file saved to :{transcript_file_path}')