import os
from pytubefix import YouTube
import urllib3

# Hides SSL warnings for school filters
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def process_raw_download():
    url = input("Paste the YouTube URL: ")
    
    print("Fetching stream data...")
    yt = YouTube(url)
    
    # 1. Choose the best audio-only stream
    audio_stream = yt.streams.get_audio_only()
    
    # 2. Let pytubefix handle the naming automatically
    # This keeps the original extension provided by YouTube
    print(f"Downloading raw audio for: {yt.title}")
    downloaded_file = audio_stream.download()
    
    print(f"File downloaded to: {downloaded_file}")
    print(f"Check this file in your folder. Does it play?")

if __name__ == "__main__":
    process_raw_download()