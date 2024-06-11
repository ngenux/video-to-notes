import pytube
def download_youtube_video(video_url, output_path):
    # Download the YouTube video
    video_id = video_url.split("=")[1]
    youtube = pytube.YouTube(video_url)
    video = youtube.streams.get_highest_resolution()
    if video.mime_type == "audio/mpeg":
        filename = f"{video_id}.mp3"  # Audio format
    else:
        filename = f"{video_id}.mp4"  # Video format (default)
    video.download(output_path,filename=filename)
    return filename

# def download_youtube_video(video_url, output_path):
#     # Download the YouTube video
#     youtube = pytube.YouTube(video_url)
#     video = youtube.streams.get_highest_resolution()
#     video.download(output_path)
# video_url = "https://www.youtube.com/watch?v=iXCqIpDZ_IY"
# output_path = "./testing"
# download_youtube_video(video_url, output_path)