import os
import requests
import re
from pytubefix import YouTube
import syncedlyrics
import urllib3

# This hides the 'InsecureRequestWarning' that pops up when bypassing school filters
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", str(name))

def process_song():
    url = input("Paste the YouTube URL: ")
    
    # 1. Get metadata using pytubefix
    print("Fetching metadata...")
    yt = YouTube(url)
    
    title = clean_filename(yt.title)
    # Pytubefix uses .author for the uploader/artist
    artist = clean_filename(yt.author)
    thumb_url = yt.thumbnail_url
    
    # Note: Pytubefix doesn't always get 'Album' metadata easily, 
    # so we'll default to just the Artist folder unless you want to add a manual input.
    album = "" 

    # 2. Build local directory structure
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "MusicLibrary")
    target_dir = os.path.join(base_dir, artist, album) if album else os.path.join(base_dir, artist)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 3. Download Audio directly to target directory
    print(f"Downloading '{title}' to {target_dir}...")
    
    # Get the highest quality audio stream (usually webm or mp4)
    audio_stream = yt.streams.get_audio_only()
    
    # Download the file
    downloaded_file = audio_stream.download(output_path=target_dir, filename=f"{title}")
    
    # Rename to .mp3 (Since we aren't using FFmpeg here, it just changes the extension)
    base, ext = os.path.splitext(downloaded_file)
    new_file = base + '.mp3'
    if os.path.exists(new_file):
        os.remove(new_file) # Remove if already exists
    os.rename(downloaded_file, new_file)
                
    # 4. Download Thumbnail (With SSL Bypass for School Wifi)
    if thumb_url:
        try:
            # Added verify=False to fix your SSLCertVerificationError
            img_data = requests.get(thumb_url, verify=False).content
            with open(os.path.join(target_dir, f"{title}.webp"), 'wb') as handler:
                handler.write(img_data)
        except Exception as e:
            print(f"Could not download thumbnail: {e}")
                
    # 5. Search Lyrics
    print("Searching for synced lyrics...")
    try:
        lrc = syncedlyrics.search(f"{artist} {title}")
        if lrc:
            with open(os.path.join(target_dir, f"{title}.lrc"), "w", encoding="utf-8") as f:
                f.write(lrc)
            print("Success! All files saved.")
        else:
            print("Audio and thumbnail saved (no synced lyrics found).")
    except Exception:
        print("Audio and thumbnail saved (Lyric search failed/blocked).")


process_song()