# player.py
import flet as ft
import vlc
import re
import asyncio
import os

def parse_lrc(lrc_content):
    lyrics = []
    pattern = r"\[(\d{2}):(\d{2})(?:[\.:](\d{2,3}))?\](.*)"
    for line in lrc_content.splitlines():
        match = re.match(pattern, line)
        if match:
            minutes, seconds, ms_part, text = match.groups()
            sec = int(minutes) * 60 + int(seconds)
            ms = float(f"0.{ms_part}") if ms_part else 0.0
            time_ms = (sec + ms) * 1000
            
            clean_text = text.strip() if text.strip() else "♪ ... ♪"
            lyrics.append({"time": time_ms, "text": clean_text})
            
    return sorted(lyrics, key=lambda x: x["time"])

def format_time(ms):
    seconds = max(0, int(ms // 1000))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"

class PlayerWidget:
    def __init__(self, page: ft.Page):
        self.page = page
        self.instance = vlc.Instance("--no-xlib", "--quiet")
        self.player = self.instance.media_player_new()
        self.lrc_data = []
        self.current_lyric_index = [-1]
        self.is_seeking = False
        
        # --- Lyric Sync Controls ---
        self.lyric_offset_ms = 0
        self.offset_input = ft.TextField(
            value="0",
            width=65,
            height=35,
            content_padding=5,
            text_align=ft.TextAlign.CENTER,
            bgcolor="#1E1E2E",
            border_color="#2A2A3D",
            focused_border_color="#6C5CE7",
            border_radius=8,
            on_change=self.on_offset_text_change
        )

        # --- UI Controls ---
        self.album_art = ft.Image(
            src="https://picsum.photos/250/250",
            width=220, height=220, fit="cover",
            border_radius=ft.border_radius.all(16)
        )
        self.art_container = ft.Container(
            content=self.album_art,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=25, color="#52000000"),
            border_radius=16, alignment=ft.Alignment(0, 0)
        )

        self.track_title = ft.Text("No Track Selected", size=22, weight="bold", color="white", text_align="center")
        self.track_artist = ft.Text("Select a song to start", size=13, color="#B3B3B3", text_align="center")

        self.lyric_display = ft.Text("Press Play", size=16, weight="w600", color="#E0E0E0", text_align="center")
        self.lyric_container = ft.Container(
            content=self.lyric_display, padding=15, bgcolor="#1E1E2E",
            border_radius=12, height=110, width=500, alignment=ft.Alignment(0, 0),
            border=ft.border.all(1, "#2A2A3D")
        )

        self.current_time_text = ft.Text("0:00", size=12, color="#8E8E93")
        self.total_time_text = ft.Text("0:00", size=12, color="#8E8E93")

        self.progress_slider = ft.Slider(
            min=0, max=1, value=0,
            active_color="#6C5CE7", inactive_color="#2D2D3F",
            on_change=lambda e: setattr(self, 'is_seeking', True),
            on_change_end=self.on_seek
        )

        # --- Dynamic Play/Pause Toggle Button ---
        self.btn_play_pause = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            icon_size=32,
            icon_color="white",
            bgcolor="#6C5CE7",
            style=ft.ButtonStyle(
                shape=ft.CircleBorder(),
                animation_duration=200  # Smooth transition animation
            ),
            on_click=self.toggle_play_pause
        )

        self.btn_stop = ft.IconButton(
            icon=ft.Icons.STOP_ROUNDED,
            icon_size=24,
            icon_color="#8E8E93",
            bgcolor="#1E1E2E",
            on_click=self.stop
        )

        self.volume_slider = ft.Slider(
            min=0, max=100, value=70, width=110,
            active_color="#6C5CE7", inactive_color="#2D2D3F",
            on_change=lambda e: self.player.audio_set_volume(int(e.control.value))
        )

        self.page.run_task(self._sync_loop)

    def toggle_play_pause(self, e=None):
        """Toggles play/pause state and updates button icon dynamically."""
        if self.player.is_playing():
            self.player.pause()
            self.btn_play_pause.icon = ft.Icons.PLAY_ARROW_ROUNDED
            self.btn_play_pause.bgcolor = "#6C5CE7"
        else:
            self.player.play()
            self.btn_play_pause.icon = ft.Icons.PAUSE_ROUNDED
            self.btn_play_pause.bgcolor = "#8C7AE6"
        
        self.btn_play_pause.update()

    def on_offset_text_change(self, e):
        val = e.control.value.strip()
        try:
            if val and val != "-":
                offset_sec = float(val)
                self.lyric_offset_ms = int(offset_sec * 1000)
                self.current_lyric_index[0] = -1
        except ValueError:
            pass

    def load_track(self, artist, album, song):
        self.player.stop()
        self.lyric_offset_ms = 0
        self.offset_input.value = "0"
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.join(script_dir, "MusicLibrary", artist, album)
        if not os.path.exists(base_dir):
            base_dir = os.path.join(script_dir, "MusicLibrary", artist, song)

        audio_path = os.path.join(base_dir, f"{song}.mp3")
        lrc_path = os.path.join(base_dir, f"{song}.lrc")
        
        webp_path = os.path.join(base_dir, "cover.webp")
        if not os.path.exists(webp_path):
            webp_path = os.path.join(base_dir, f"{song}.webp")

        self.album_art.src = webp_path if os.path.exists(webp_path) else "https://picsum.photos/250/250"
        self.track_title.value = song
        self.track_artist.value = f"{artist}" if artist == album else f"{artist} • {album}"
        self.lyric_display.value = "Loading lyrics..."

        if os.path.exists(audio_path):
            media = self.instance.media_new(audio_path)
            self.player.set_media(media)

        self.lrc_data = []
        found_lrc = lrc_path if os.path.exists(lrc_path) else None
        
        if not found_lrc and os.path.exists(base_dir):
            for file in os.listdir(base_dir):
                if file.endswith(".lrc"):
                    found_lrc = os.path.join(base_dir, file)
                    break

        if found_lrc and os.path.exists(found_lrc):
            with open(found_lrc, "r", encoding="utf-8") as f:
                self.lrc_data = parse_lrc(f.read())
            self.lyric_display.value = "Ready to play"
        else:
            self.lyric_display.value = "No synced lyrics available"

        self.current_lyric_index[0] = -1
        
        # Start playback & update toggle button to Pause state
        self.player.play()
        self.btn_play_pause.icon = ft.Icons.PAUSE_ROUNDED
        self.btn_play_pause.bgcolor = "#8C7AE6"
        self.page.update()

    def on_seek(self, e):
        if self.player.get_length() > 0:
            target = int(float(e.control.value) * self.player.get_length())
            self.player.set_time(target)
            self.current_lyric_index[0] = -1
        self.is_seeking = False

    def stop(self, e=None):
        self.player.stop()
        self.lyric_display.value = "Press Play"
        self.progress_slider.value = 0
        self.current_time_text.value = "0:00"
        self.btn_play_pause.icon = ft.Icons.PLAY_ARROW_ROUNDED
        self.btn_play_pause.bgcolor = "#6C5CE7"
        self.page.update()

    async def _sync_loop(self):
        while True:
            if self.player.is_playing():
                pos = self.player.get_time()
                dur = self.player.get_length()

                if pos > 0:
                    self.current_time_text.value = format_time(pos)
                    if dur > 0:
                        self.total_time_text.value = format_time(dur)
                        if not self.is_seeking:
                            self.progress_slider.value = min(pos / dur, 1.0)

                    adjusted_pos = pos - self.lyric_offset_ms
                    if self.lrc_data:
                        for i in range(len(self.lrc_data)):
                            if self.lrc_data[i]["time"] <= adjusted_pos:
                                if i == len(self.lrc_data) - 1 or adjusted_pos < self.lrc_data[i+1]["time"]:
                                    if self.current_lyric_index[0] != i:
                                        self.current_lyric_index[0] = i
                                        self.lyric_display.value = self.lrc_data[i]["text"]
            self.page.update()
            await asyncio.sleep(0.05)

    def get_widget(self):
        return ft.Container(
            content=ft.Column([
                self.art_container,
                self.track_title,
                self.track_artist,
                ft.Container(height=5),
                
                # Lyrics Box
                self.lyric_container,
                
                # Sync Offset Text Input Row
                ft.Row([
                    ft.Icon(ft.Icons.TIMER_ROUNDED, size=16, color="#8E8E93"),
                    ft.Text("Sync Offset (sec):", size=12, color="#8E8E93"),
                    self.offset_input,
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),

                # Seek Bar & Timers
                ft.Column([
                    self.progress_slider,
                    ft.Row([self.current_time_text, self.total_time_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], spacing=0),

                # Control Buttons & Volume (Unified Play/Pause Button)
                ft.Row([
                    ft.Row([self.btn_stop, self.btn_play_pause], spacing=12),
                    ft.Row([ft.Icon(ft.Icons.VOLUME_UP, size=16, color="#8E8E93"), self.volume_slider])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            padding=15
        )