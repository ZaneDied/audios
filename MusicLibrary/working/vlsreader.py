import flet as ft
import vlc
import re
import asyncio
import os

# 1. Simple LRC Parser
def parse_lrc(lrc_content):
    lyrics = []
    pattern = r"\[(\d{2}):(\d{2}\.\d{2,})\](.*)"
    for line in lrc_content.splitlines():
        match = re.match(pattern, line)
        if match:
            minutes, seconds, text = match.groups()
            time_ms = (int(minutes) * 60 + float(seconds)) * 1000
            lyrics.append({"time": time_ms, "text": text.strip()})
    return sorted(lyrics, key=lambda x: x["time"])

def main(page: ft.Page):
    page.title = "LRC Sync Player"

    # Dynamic path construction
    base_dir = os.path.join(os.getcwd(), "MusicLibrary")
    artist = "Tyler, The Creator - Topic"
    album = "See You Again"
    song = "See You Again"

    audio_path = os.path.join(base_dir, artist, album, f"{song}.mp3")
    lrc_path = os.path.join(base_dir, artist, album, f"{song}.lrc")

    # Initialize VLC with flags to handle fragmented/discontinuous streams
    instance = vlc.Instance("--no-xlib", "--quiet") 
    player = instance.media_player_new()
    media = instance.media_new(audio_path)
    player.set_media(media)

    lrc_data = []
    if os.path.exists(lrc_path):
        with open(lrc_path, "r", encoding="utf-8") as f:
            lrc_data = parse_lrc(f.read())

    lyric_display = ft.Text("Press Play", size=32, weight="bold", text_align=ft.TextAlign.CENTER)
    time_display = ft.Text("00:00", size=12)
    volume_slider = ft.Slider(min=0, max=100, value=70, width=200, 
                              on_change=lambda e: player.audio_set_volume(int(e.control.value)))
    progress_slider = ft.Slider(min=0, max=1, value=0, width=300)
    current_lyric_index = [-1]

    async def sync_loop():
        while True:
            if player.is_playing():
                current_pos = player.get_time()
                seconds = int(current_pos // 1000)
                time_display.value = f"{seconds // 60:02d}:{seconds % 60:02d}"
                
                if lrc_data:
                    total_duration = lrc_data[-1]["time"]
                    if total_duration > 0:
                        progress_slider.value = min(current_pos / total_duration, 1.0)
                    for i in range(len(lrc_data)):
                        if lrc_data[i]["time"] <= current_pos:
                            if i == len(lrc_data) - 1 or current_pos < lrc_data[i+1]["time"]:
                                if current_lyric_index[0] != i:
                                    current_lyric_index[0] = i
                                    lyric_display.value = lrc_data[i]["text"]
                page.update()
            await asyncio.sleep(0.05)

    page.run_task(sync_loop)

    page.add(
        ft.Row([
            ft.Container(
                ft.Column([
                    ft.Text("LRC Sync Player", size=28, weight="bold"),
                    ft.Divider(),
                    ft.Container(
                        lyric_display,
                        padding=30,
                        bgcolor="#455a64",
                        border_radius=10,
                        height=160,
                        width=600,
                        alignment=ft.Alignment(0, 0)
                    ),
                    time_display,
                    progress_slider,
                    ft.Row([
                        ft.Button("Play", on_click=lambda _: player.play()),
                        ft.Button("Pause", on_click=lambda _: player.pause()),
                        ft.Button("Stop", on_click=lambda _: player.stop()),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([
                        ft.Text("Volume:", size=12),
                        volume_slider,
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.START, spacing=15),
                padding=20
            )
        ], alignment=ft.MainAxisAlignment.CENTER)
    )

ft.run(main)