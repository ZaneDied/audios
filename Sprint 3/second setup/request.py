# request.py
import os
import requests
import re
import asyncio
from pytubefix import YouTube
import syncedlyrics
import urllib3

# Disable SSL warnings for restricted/school networks
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def clean_filename(name):
    """Removes invalid OS characters from filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", str(name)).strip()

def download_youtube_track(url: str):
    """
    Downloads audio, thumbnail (.webp), and synced lyrics (.lrc) from YouTube URL.
    Returns (artist, title) upon success.
    """
    if not url or "youtube.com" not in url and "youtu.be" not in url:
        raise ValueError("Please provide a valid YouTube URL!")

    print(f"Fetching metadata for: {url}")
    yt = YouTube(url)
    title = clean_filename(yt.title)
    artist = clean_filename(yt.author)
    thumb_url = yt.thumbnail_url

    # Target directory: MusicLibrary / Artist / SongTitle /
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "MusicLibrary")
    target_dir = os.path.join(base_dir, artist, title)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 1. Download Audio Track
    audio_stream = yt.streams.get_audio_only()
    audio_filename = f"{title}.mp3"
    audio_stream.download(output_path=target_dir, filename=audio_filename)

    # 2. Download Album Artwork (.webp)
    if thumb_url:
        try:
            img_data = requests.get(thumb_url, verify=False).content
            with open(os.path.join(target_dir, "cover.webp"), 'wb') as handler:
                handler.write(img_data)
        except Exception as e:
            print(f"Thumbnail download skipped: {e}")

    # 3. Fetch Synced Lyrics (.lrc)
    try:
        lrc = syncedlyrics.search(f"{artist} {title}")
        if lrc:
            with open(os.path.join(target_dir, f"{title}.lrc"), "w", encoding="utf-8") as f:
                f.write(lrc)
    except Exception as e:
        print(f"Lyrics search skipped: {e}")

    return artist, title