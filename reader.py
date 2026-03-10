import flet as ft
import pygame
import re
import time
import asyncio

# 1. Simple LRC Parser
def parse_lrc(lrc_content):
    lyrics = []
    # Pattern to match [MM:SS.xx]Text
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
    
    # UPDATE THESE PATHS TO YOUR ACTUAL FILE LOCATIONS
    audio_path = r"C:\Users\Zane & Zion\Desktop\whatever\audios\MusicLibrary\Luci4\Hey\Hey.mp3"
    lrc_path = r"C:\Users\Zane & Zion\Desktop\whatever\audios\MusicLibrary\Luci4\Hey\Hey.lrc"
    
    # Initialize pygame mixer for audio playback
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    
    with open(lrc_path, "r", encoding="utf-8") as f:
        lrc_data = parse_lrc(f.read())
    
    lyric_display = ft.Text("Press Play", size=24, weight="bold")
    time_display = ft.Text("00:00", size=12)
    volume_slider = ft.Slider(min=0, max=100, value=70, width=200, on_change=lambda e: pygame.mixer.music.set_volume(e.control.value / 100))
    progress_slider = ft.Slider(min=0, max=1, value=0, width=300)
    current_lyric_index = [-1]  # Use list to allow modification in nested function
    is_updating = [False]  # Flag to prevent rapid updates
    
    def update_volume(e):
        pygame.mixer.music.set_volume(e.control.value / 100)
    
    volume_slider.on_change = update_volume
    
    async def sync_loop():
        while True:
            try:
                if pygame.mixer.music.get_busy():
                    # Get current position in milliseconds
                    current_pos = pygame.mixer.music.get_pos()
                    
                    # Update time display
                    seconds = int(current_pos // 1000)
                    mins = seconds // 60
                    secs = seconds % 60
                    time_display.value = f"{mins:02d}:{secs:02d}"
                    
                    # Update progress slider
                    if lrc_data:
                        total_duration = lrc_data[-1]["time"]
                        if total_duration > 0:
                            progress_slider.value = min(current_pos / total_duration, 1.0)
                    
                    # Find and update the current lyric
                    for i in range(len(lrc_data)):
                        if lrc_data[i]["time"] <= current_pos:
                            if i + 1 < len(lrc_data) and current_pos < lrc_data[i+1]["time"]:
                                if current_lyric_index[0] != i:
                                    current_lyric_index[0] = i
                                    lyric_display.value = lrc_data[i]["text"]
                            else:
                                if i == len(lrc_data) - 1 and current_lyric_index[0] != i:
                                    current_lyric_index[0] = i
                                    lyric_display.value = lrc_data[i]["text"]
                    
                    page.update()
                else:
                    time_display.value = "00:00"
                    lyric_display.value = "Press Play"
                    page.update()
            except Exception as e:
                print(f"Sync loop error: {e}")
            
            await asyncio.sleep(0.05)  # Sync every 50ms for smoother updates

    # Start the sync loop as an async task in Flet's event loop
    page.run_task(sync_loop)

    page.add(
        ft.Container(
            ft.Column([
                ft.Text("LRC Sync Player", size=28, weight="bold"),
                ft.Divider(),
                
                # Lyrics Display
                ft.Container(
                    lyric_display,
                    padding=20,
                    bgcolor="#455a64",
                    border_radius=10,
                    height=100,
                    width=400,
                    alignment=ft.Alignment(0, 0)
                ),
                
                # Time Display
                time_display,
                
                # Progress Bar
                progress_slider,
                
                # Playback Controls
                ft.Row([
                    ft.Button("Play", on_click=lambda _: pygame.mixer.music.play()),
                    ft.Button("Pause", on_click=lambda _: pygame.mixer.music.pause()),
                    ft.Button("Stop", on_click=lambda _: pygame.mixer.music.stop()),
                ], alignment=ft.MainAxisAlignment.CENTER),
                
                # Volume Control
                ft.Row([
                    ft.Text("Volume:", size=12),
                    volume_slider,
                    ft.Text(f"{int(volume_slider.value)}%", size=12, width=30)
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.START, spacing=15),
            padding=20
        )
    )

ft.run(main)