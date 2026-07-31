# Setup & Running Instructions

> **Note:** This project uses **VLC** (`python-vlc`) instead of Pygame for audio playback to support media streaming and accurate synced lyrics.

---

## Setup Steps

### 1. Install System Dependencies (Windows)

VLC Media Player is required for the audio engine, and FFmpeg is required to process downloaded YouTube audio. Run these commands in your Command Prompt or Terminal:

```cmd
winget install VideoLAN.VLC
winget install ffmpeg
```

*(Restart your terminal after running these commands so the system PATH updates.)*

---

### 2. Install Required Python Packages

> **Important Flet Version Requirement:** > * For **Sprint 1 and Sprint 2 and setup version in Sprint 3**, use `flet==0.82.2`.
> * For the **Final Sprint 3 version**, install `flet==0.21.2` to ensure full UI compatibility and prevent framework module errors.

Run the following command for the final version:

```bash
pip install "flet==0.21.2" python-vlc Pillow requests pytubefix syncedlyrics urllib3 certifi
```

*(If you are setting up or testing Sprint 1/2 environments, install `flet==0.82.2` instead).*

---

### 3. Run the Application

Once all dependencies are installed, navigate to your project directory and start the final app:

```bash
python main.py
```

---

## How to Use the Music Player

1. **Open the Library / Search Bar:**
   * Click the **Browse** button on the bottom control bar to open the top drawer.
   * You will see your local music library listed.

2. **Download New Songs:**
   * Paste a YouTube URL into the search/input bar at the top of the Browse drawer.
   * Click **Download**. The player will automatically fetch the audio, album artwork, and synced lyrics (`.lrc`) into your `MusicLibrary` folder and start playing the track.

3. **Select & Play Songs:**
   * Click on any song in your library list to start playing it. 
   * Click the **Play/Pause** button on the bottom bar to pause or resume playback.
   * Use the **Progress Slider** to seek or fast-forward to any part of the song.

4. **Lyrics & Visual Theme:**
   * Synchronized lyrics will automatically display and center on the right side of the screen as the song plays.
   * The background color behind the lyrics automatically adjusts to match the main colors of the current song's album art.
   * Use the **Timer Offset** field (located next to the volume slider) to adjust lyric delay in seconds if lyrics are slightly out of sync.
