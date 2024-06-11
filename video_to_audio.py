import logging
from moviepy.editor import VideoFileClip

def extract_audio_from_video(video_file_path, audio_file_path):
    """
    Extracts audio from a video file and saves it to an audio file in MP3 format.

    Parameters:
    video_file_path (str): The path to the video file.
    audio_file_path (str): The path where the extracted audio will be saved.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    video = None
    audio = None
    
    try:
        logging.info(f"Loading video file: {video_file_path}")
        # Load the video file
        video = VideoFileClip(video_file_path)
        
        logging.info("Extracting audio from video")
        # Extract the audio
        audio = video.audio
        
        logging.info(f"Saving extracted audio to: {audio_file_path}")
        # Write the audio to a file in MP3 format
        audio.write_audiofile(audio_file_path, codec='mp3')
        
        logging.info("Audio extraction and saving completed successfully")
    except Exception as e:
        logging.error(f"An error occurred while processing: {e}")
    finally:
        # Close the audio and video clips if they were opened
        if audio:
            try:
                audio.close()
                logging.info("Closed audio clip")
            except Exception as e:
                logging.warning(f"Could not close audio clip: {e}")
        if video:
            try:
                video.close()
                logging.info("Closed video clip")
            except Exception as e:
                logging.warning(f"Could not close video clip: {e}")

# Example usage
video_file_path = r"C:\Users\MohammedKareemKhan\Desktop\new_fldr\testing\addition.mp4"
audio_file_path = r"Cvideo-to-notes\audio_from video\addition.mp3"
extract_audio_from_video(video_file_path, audio_file_path)

