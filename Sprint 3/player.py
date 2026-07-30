# player.py
import flet as ft
import vlc
import re
import asyncio
import os
from PIL import Image

def get_average_color(image_path_or_url, fallback_color="#5B1D1D"):
    """Calculates average color by resizing image to 1x1 pixel."""
    try:
        if not os.path.exists(image_path_or_url):
            return fallback_color

        with Image.open(image_path_or_url) as img:
            img = img.convert("RGB")
            # Resizing to 1x1 averages all pixel colors
            img = img.resize((1, 1))
            r, g, b = img.getpixel((0, 0))
            
            # Optional: Dim the color slightly so text stays high-contrast
            r, g, b = int(r * 0.4), int(g * 0.4), int(b * 0.4)
            
            return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return fallback_color
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
    def __init__(self, page: ft.Page, browse_widget=None):
        self.page = page
        self.instance = vlc.Instance("--no-xlib", "--quiet")
        self.player = self.instance.media_player_new()
        self.lrc_data = []
        self.current_lyric_index = [-1]
        self.is_seeking = False
        self.browse_widget = browse_widget

        # --- Geometry for Exact Centering ---
        self.LINE_HEIGHT = 50       # Fixed height per lyric block
        self.CENTER_OFFSET = 220    # Pixel distance from top to screen center

        # --- Left Panel Controls ---
        self.track_title = ft.Text("No Track Selected", size=24, weight="bold", color="white")
        self.track_artist = ft.Text("Select a song from Browse", size=14, color="#B3B3B3")

        self.album_art = ft.Image(
            src="https://picsum.photos/300/300",
            width=280, height=280, fit="cover",
            border_radius=ft.border_radius.all(24)
        )
        self.art_container = ft.Container(
            content=self.album_art,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=25, color="#52000000"),
            border_radius=24,
            alignment=ft.Alignment(0, 0)
        )

        # --- Right Panel Controls (Position Animated Lyrics) ---
        self.lyrics_list_column = ft.Column(
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.START
        )
        
        # Container that slides vertically via smooth position animation
        self.animated_lyrics_box = ft.Container(
            content=self.lyrics_list_column,
            top=self.CENTER_OFFSET,
            left=0,
            right=0,
            animate_position=ft.Animation(450, ft.AnimationCurve.DECELERATE)
        )

        self.lyrics_container = ft.Container(
            content=ft.Stack([self.animated_lyrics_box]),
            padding=ft.padding.symmetric(horizontal=40),
            bgcolor="#5B1D1D",  # Dark Burgundy background
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            expand=True
        )

        # --- Bottom Player Bar Controls ---
        self.current_time_text = ft.Text("0:00", size=12, color="#B3B3B3")
        self.total_time_text = ft.Text("0:00", size=12, color="#B3B3B3")

        self.progress_slider = ft.Slider(
            min=0, max=1, value=0,
            active_color="white", inactive_color="#4D4D4D",
            on_change=lambda e: setattr(self, 'is_seeking', True),
            on_change_end=self.on_seek,
            expand=True
        )

        self.btn_play_pause = ft.IconButton(
            icon=ft.Icons.PLAY_CIRCLE_FILL_ROUNDED,
            icon_size=42,
            icon_color="white",
            on_click=self.toggle_play_pause
        )

        self.lyric_offset_ms = 0
        self.offset_input = ft.TextField(
            value="0", width=50, height=32, content_padding=2,
            text_align=ft.TextAlign.CENTER, bgcolor="#181818",
            border_color="#282828", focused_border_color="#6C5CE7",
            border_radius=6, text_size=12,
            on_change=self.on_offset_text_change
        )

        self.volume_slider = ft.Slider(
            min=0, max=100, value=70, width=90,
            active_color="white", inactive_color="#4D4D4D",
            on_change=lambda e: self.player.audio_set_volume(int(e.control.value))
        )

        # --- Hidden Collapsible Browse Drawer ---
        self.browse_drawer = ft.Container(
            content=self.browse_widget,
            visible=False,
            padding=15,
            bgcolor="#121212",
            border_radius=12,
            border=ft.border.all(1, "#282828")
        )

        self.btn_browse = ft.TextButton(
            "Browse",
            style=ft.ButtonStyle(color="white"),
            on_click=self.toggle_browse_drawer
        )

        self.page.run_task(self._sync_loop)

    def toggle_browse_drawer(self, e=None):
        self.browse_drawer.visible = not self.browse_drawer.visible
        self.browse_drawer.update()

    def toggle_play_pause(self, e=None):
        if self.player.is_playing():
            self.player.pause()
            self.btn_play_pause.icon = ft.Icons.PLAY_CIRCLE_FILL_ROUNDED
        else:
            self.player.play()
            self.btn_play_pause.icon = ft.Icons.PAUSE_CIRCLE_FILLED_ROUNDED
        self.btn_play_pause.update()

    def on_offset_text_change(self, e):
        val = e.control.value.strip()
        try:
            if val and val != "-":
                self.lyric_offset_ms = int(float(val) * 1000)
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
            webp_path = os.path.join(base_dir, f"{song}.jpg")
        if not os.path.exists(webp_path):
            webp_path = os.path.join(base_dir, f"{song}.webp")

        # Set cover art source
        if os.path.exists(webp_path):
            self.album_art.src = webp_path
            # Dynamic background color from album art!
            avg_color = get_average_color(webp_path)
            self.lyrics_container.bgcolor = avg_color
        else:
            self.album_art.src = "https://picsum.photos/300/300"
            self.lyrics_container.bgcolor = "#5B1D1D"

        self.track_title.value = song
        self.track_artist.value = f"{artist}" if artist == album else f"{artist} • {album}"

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
            self.render_lyrics_list()
        else:
            self.lyrics_list_column.controls = [
                ft.Text("No synced lyrics available", size=18, color="#8E8E93")
            ]
            self.animated_lyrics_box.top = self.CENTER_OFFSET

        self.current_lyric_index[0] = -1
        self.player.play()
        self.btn_play_pause.icon = ft.Icons.PAUSE_CIRCLE_FILLED_ROUNDED
        self.page.update()

    def render_lyrics_list(self):
        """Creates each lyric block with exact fixed heights and medium-weight inactive font."""
        self.lyrics_list_column.controls.clear()

        for idx, line in enumerate(self.lrc_data):
            self.lyrics_list_column.controls.append(
                ft.Container(
                    content=ft.Text(
                        line["text"],
                        size=22,
                        weight=ft.FontWeight.W_500,  # Fuller font weight for unactive lines
                        color="#B0B0B0",             # Bright, clean gray
                        animate_opacity=200
                    ),
                    height=self.LINE_HEIGHT,
                    alignment=ft.Alignment(-1, 0)
                )
            )
        self.animated_lyrics_box.top = self.CENTER_OFFSET

    def update_active_lyric(self, active_index):
        """Highlights the active line and slides the entire container so active_index is centered."""
        for idx in range(len(self.lrc_data)):
            container = self.lyrics_list_column.controls[idx]
            txt = container.content
            if idx == active_index:
                txt.weight = ft.FontWeight.BOLD
                txt.size = 28
                txt.color = "#FFFFFF"
                txt.opacity = 1.0
            else:
                txt.weight = ft.FontWeight.W_500
                txt.size = 22
                txt.color = "#B0B0B0"
                txt.opacity = 0.75

        # Calculate position so active_index lands directly at CENTER_OFFSET
        self.animated_lyrics_box.top = self.CENTER_OFFSET - (active_index * self.LINE_HEIGHT)
        
        if self.lyrics_container.page:
            self.lyrics_container.update()

    def on_seek(self, e):
        if self.player.get_length() > 0:
            target = int(float(e.control.value) * self.player.get_length())
            self.player.set_time(target)
            self.current_lyric_index[0] = -1
        self.is_seeking = False

    def stop(self, e=None):
        self.player.stop()
        self.progress_slider.value = 0
        self.current_time_text.value = "0:00"
        self.btn_play_pause.icon = ft.Icons.PLAY_CIRCLE_FILL_ROUNDED
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
                                        self.update_active_lyric(i)
                self.page.update()
            await asyncio.sleep(0.05)

    def get_widget(self):
        left_panel = ft.Container(
            content=ft.Column([
                ft.Column([self.track_title, self.track_artist], spacing=4),
                ft.Container(height=20),
                self.art_container,
            ], alignment=ft.MainAxisAlignment.START),
            padding=30,
            bgcolor="#121212",
            width=360
        )

        main_content_row = ft.Row([
            left_panel,
            self.lyrics_container
        ], expand=True, spacing=0)

        bottom_player_bar = ft.Container(
            content=ft.Column([
                ft.Row([
                    self.current_time_text,
                    self.progress_slider,
                    self.total_time_text,
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),

                ft.Row([
                    self.btn_browse,
                    self.btn_play_pause,
                    ft.Row([
                        ft.Icon(ft.Icons.TIMER_ROUNDED, size=14, color="#8E8E93"),
                        self.offset_input,
                        ft.Container(width=10),
                        ft.Icon(ft.Icons.VOLUME_UP_ROUNDED, size=16, color="#8E8E93"),
                        self.volume_slider
                    ], alignment=ft.MainAxisAlignment.END, spacing=5)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=0),
            padding=ft.padding.only(left=20, right=20, top=5, bottom=10),
            bgcolor="#000000",
            height=95
        )

        return ft.Column([
            self.browse_drawer,
            main_content_row,
            bottom_player_bar
        ], expand=True, spacing=0)