import os
import requests
import re
from pytubefix import YouTube
import syncedlyrics
import urllib3

# Hides SSL warnings for school networks
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def clean_filename(name):
    # Removes characters that are not allowed in Windows file names
    return re.sub(r'[\\/*?:"<>|]', "", str(name)).strip()

def process_song():
    url = input("Paste the YouTube URL: ")
    
    print("Fetching metadata...")
    try:
        yt = YouTube(url)
        title = clean_filename(yt.title)
        artist = clean_filename(yt.author)
        thumb_url = yt.thumbnail_url
    except Exception as e:
        print(f"Error connecting to YouTube: {e}")
        return
    
    # 1. Build the directory structure: MusicLibrary / Artist Name / Song Title
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "MusicLibrary")
    target_dir = os.path.join(base_dir, artist, title)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 2. Download Audio
    print(f"Downloading '{title}' to {target_dir}...")
    try:
        audio_stream = yt.streams.get_audio_only()
        
        # Determine extension from the stream's MIME type (e.g., audio/webm -> webm)
        ext = audio_stream.mime_type.split('/')[-1]
        filename = f"{title}.mp3"
        
        # Download with explicit extension
        audio_stream.download(output_path=target_dir, filename=filename)
        print(f"Successfully downloaded: {filename}")
    except Exception as e:
        print(f"Audio download failed: {e}")
        return
                
    # 3. Download Thumbnail (SSL Bypass for school)
    if thumb_url:
        try:
            img_data = requests.get(thumb_url, verify=False).content
            with open(os.path.join(target_dir, f"{title}.webp"), 'wb') as handler:
                handler.write(img_data)
        except Exception:
            print("Thumbnail download blocked by network.")
                
    # 4. Search Lyrics
    print(f"Searching for lyrics for {artist} - {title}...")
    try:
        lrc = syncedlyrics.search(f"{artist} {title}")
        if lrc:
            with open(os.path.join(target_dir, f"{title}.lrc"), "w", encoding="utf-8") as f:
                f.write(lrc)
            print("Success! Folder created with audio, Thumbnail, and Lyrics.")
        else:
            print(f"Saved to {target_dir} (no lyrics found).")
    except Exception:
        print("Lyric search failed.")

if __name__ == "__main__":
    while True:
        process_song()
        if input("\nProcess another? (y/n): ").lower() != 'y':
            break