import streamlit as st
from download import download_youtube_video
import boto3
import os
from dotenv import load_dotenv

load_dotenv()
key = os.environ["KEY"]
s_key = os.environ["S_KEY"]
b_name = os.environ["B_NAME"]
r_name = os.environ["REGION_NAME"]

def upload_to_s3(file, bucket_name, object_name):
    s3_client = boto3.client(
        's3',
        region_name=r_name,
        aws_access_key_id=key,
        aws_secret_access_key=s_key
    )
    try:
        s3_client.upload_fileobj(file, bucket_name, object_name)
        st.success(f"File successfully uploaded to {bucket_name}/{object_name}")
    except Exception as e:
        st.error(f"Error uploading file: {e}")

with st.sidebar:
    url_input = st.text_input(label="Paste YouTube URL")
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov", "mkv"])
    get_video_button = st.button("Get Video")

# Directory to save downloaded videos
output_path = "./downloads"
if not os.path.exists(output_path):
    os.makedirs(output_path)

video_bytes = None

# Handle YouTube video download
if get_video_button:
    if url_input:
        video_file_name = download_youtube_video(url_input, output_path)
        video_file_path = os.path.join(output_path, video_file_name)
        if os.path.exists(video_file_path):
            with open(video_file_path, 'rb') as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)
                if st.button("Upload Downloaded Video to S3"):
                    with open(video_file_path, 'rb') as video_file:
                        upload_to_s3(video_file, b_name, video_file_name)
    else:
        st.error("Please provide a valid YouTube URL")

# Handle file upload and display
if uploaded_file is not None:
    st.video(uploaded_file)
    
    if st.button("Upload Selected Video to S3"):
        file_details = {
            "filename": uploaded_file.name,
            "filetype": uploaded_file.type,
            "filesize": uploaded_file.size
        }
        # st.write(file_details)
        folder_path = 'video-content/'
        object_name = folder_path + uploaded_file.name
        upload_to_s3(uploaded_file, b_name, object_name)

#////////////////////////////////////////////////////////////////////////////////////////////////////////
