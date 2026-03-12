import os
import requests
import re
from pytubefix import YouTube
import syncedlyrics
import urllib3

# Hides the SSL warnings from school filters
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", str(name))

def process_song():
    url = input("Paste the YouTube URL: ")
    
    print("Fetching metadata...")
    yt = YouTube(url)
    
    title = clean_filename(yt.title)
    artist = clean_filename(yt.author)
    thumb_url = yt.thumbnail_url
    
    # --- ALBUM LOGIC START ---
    # Check if metadata has album, otherwise ask the user
    metadata = yt.metadata.metadata
    album = ""
    
    # Try to find 'Album' in the YouTube metadata list
    if metadata:
        for item in metadata:
            if 'Album' in item:
                album = clean_filename(item['Album'])
                break
    
    # If it's still empty, ask you! (Press Enter to skip)
    if not album:
        album = input(f"Album name not found for '{title}'. Enter album name (or press Enter to skip): ").strip()
        album = clean_filename(album)
    # --- ALBUM LOGIC END ---

    # 2. Build local directory structure
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "MusicLibrary")
    
    # Only create the album subfolder if 'album' is not empty
    if album:
        target_dir = os.path.join(base_dir, artist, album)
    else:
        target_dir = os.path.join(base_dir, artist)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 3. Download Audio
    print(f"Downloading '{title}'...")
    audio_stream = yt.streams.get_audio_only()
    downloaded_file = audio_stream.download(output_path=target_dir, filename=f"{title}")
    
    # Rename to .mp3
    base, ext = os.path.splitext(downloaded_file)
    new_file = base + '.mp3'
    if os.path.exists(new_file):
        os.remove(new_file)
    os.rename(downloaded_file, new_file)
                
    # 4. Download Thumbnail (SSL Bypass)
    if thumb_url:
        try:
            img_data = requests.get(thumb_url, verify=False).content
            with open(os.path.join(target_dir, f"{title}.webp"), 'wb') as handler:
                handler.write(img_data)
        except Exception:
            print("Thumbnail download blocked/failed.")
                
    # 5. Search Lyrics
    print(f"Searching for lyrics for {artist} - {title}...")
    try:
        lrc = syncedlyrics.search(f"{artist} {title}")
        if lrc:
            with open(os.path.join(target_dir, f"{title}.lrc"), "w", encoding="utf-8") as f:
                f.write(lrc)
            print("Success! Everything saved.")
        else:
            print("Audio/Thumb saved (lyrics not found).")
    except Exception:
        print("Lyric search failed.")

process_song()