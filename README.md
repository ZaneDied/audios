# Setup & Running Instructions

Note: This project uses **VLC** (`python-vlc`) instead of Pygame for audio playback to support media streaming and accurate synced lyrics.

---

## 1. Install System Dependencies (Windows)

VLC Media Player is required for the audio engine, and FFmpeg is required to process downloaded YouTube audio. Run these commands in your command prompt or terminal:

```cmd
winget install VideoLAN.VLC
winget install ffmpeg

pip install flet python-vlc Pillow requests pytubefix syncedlyrics urllib3

python main.py -- to run the final program from sprint 3