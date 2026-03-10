import yt_dlp
import syncedlyrics
import os
import requests
import re

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def process_song():
    url = input("Paste the YouTube URL: ")
    
    # 1. Get metadata first to build the directory
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = clean_filename(info.get('title', 'Unknown Title'))
        artist = clean_filename(info.get('artist', 'Unknown Artist') or info.get('uploader', 'Unknown Artist'))
        album = clean_filename(info.get('album', ''))
        thumb_url = info.get('thumbnail')

    # 2. Build local directory structure
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "MusicLibrary")
    target_dir = os.path.join(base_dir, artist, album) if album else os.path.join(base_dir, artist)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 3. Download Audio directly to target directory
    print(f"Downloading '{title}' to {target_dir}...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'outtmpl': os.path.join(target_dir, f"{title}.%(ext)s"),
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
                
    # 4. Download Thumbnail
    if thumb_url:
        img_data = requests.get(thumb_url).content
        with open(os.path.join(target_dir, f"{title}.webp"), 'wb') as handler:
            handler.write(img_data)
                
    # 5. Search Lyrics
    print("Searching for synced lyrics...")
    lrc = syncedlyrics.search(f"{artist} {title}")
    if lrc:
        with open(os.path.join(target_dir, f"{title}.lrc"), "w", encoding="utf-8") as f:
            f.write(lrc)
        print("Success! All files saved.")
    else:
        print("Audio and thumbnail saved (no synced lyrics found).")


process_song()