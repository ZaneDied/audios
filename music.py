import yt_dlp
import syncedlyrics
import os
import re

def clean_title(title):
    # Removes text inside () or [] to make searching easier
    return re.sub(r'\([^)]*\)|\[[^\]]*\]', '', title).strip()

def process_song():
    url = input("Paste the YouTube URL: ")
    
    # 1. Download
    print("Downloading audio...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'outtmpl': 'song.%(ext)s',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'Unknown Title')
        
    # 2. Lyrics
    print(f"Searching for lyrics for: {title}")
    query = clean_title(title)
    lrc = syncedlyrics.search(query)
    
    if lrc:
        with open("song.lrc", "w", encoding="utf-8") as f:
            f.write(lrc)
        print("Success! song.mp3 and song.lrc are saved.")
    else:
        print("Audio downloaded, but no synced lyrics were found.")

process_song()