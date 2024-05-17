import streamlit as st
from download import download_youtube_video

with st.sidebar:
    url_input = st.text_input(label = "paste url")
    get_video_button = st.button("Get Video")
output_path = "./downloads"
if get_video_button:
    video_file_name = download_youtube_video(url_input,output_path)
    video_file = open(f'C:/Users/SrikanthBachannagari/Documents/Projects/video-to-notes/downloads/{video_file_name}', 'rb')
    video_bytes = video_file.read()

st.video(video_bytes)
