import os
import requests
import re
from pytubefix import YouTube
import syncedlyrics
import urllib3

# Hides the SSL warnings from school filters
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def clean_filename(name):
    # Removes characters that aren't allowed in Windows folder/file names
    return re.sub(r'[\\/*?:"<>|]', "", str(name)).strip()

def process_song():
    url = input("Paste the YouTube URL: ")
    
    print("Fetching metadata...")
    yt = YouTube(url)
    
    # Get the basic info
    title = clean_filename(yt.title)
    artist = clean_filename(yt.author)
    thumb_url = yt.thumbnail_url
    
    # 1. Build the directory structure
    # Path: MusicLibrary / Artist Name / Song Title
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "MusicLibrary")
    target_dir = os.path.join(base_dir, artist, title)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 2. Download Audio
    print(f"Downloading '{title}' to {target_dir}...")
    audio_stream = yt.streams.get_audio_only()
    
    # Download as the raw format first
    downloaded_file = audio_stream.download(output_path=target_dir, filename=f"{title}")
    
    # Rename to .mp3 extension
    base, ext = os.path.splitext(downloaded_file)
    new_file = base + '.mp3'
    if os.path.exists(new_file):
        os.remove(new_file)
    os.rename(downloaded_file, new_file)
                
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
            print("Success! Folder created with MP3, Thumbnail, and Lyrics.")
        else:
            print(f"Saved to {target_dir} (but no lyrics found).")
    except Exception:
        print("Lyric search failed.")


process_song()