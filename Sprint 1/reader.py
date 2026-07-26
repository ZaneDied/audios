import flet as ft
import pygame
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
    artist = "Tyler， The Creator, Frank Ocean"
    album = "Flower Boy"
    song = "Where This Flower Blooms"

    audio_path = os.path.join(base_dir, artist, album, f"{song}.mp3")
    lrc_path = os.path.join(base_dir, artist, album, f"{song}.lrc")

    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)

    with open(lrc_path, "r", encoding="utf-8") as f:
        lrc_data = parse_lrc(f.read())

    lyric_display = ft.Text("Press Play", size=32, weight="bold", text_align=ft.TextAlign.CENTER)
    current_lyric_index = [-1]

    async def sync_loop():
        while True:
            try:
                if pygame.mixer.music.get_busy():
                    current_pos = pygame.mixer.music.get_pos()
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
                    lyric_display.value = "Press Play"
                    page.update()
            except Exception as e:
                print(f"Sync loop error: {e}")
            await asyncio.sleep(0.05)

    page.run_task(sync_loop)

    # Simplified layout: Just lyrics card and a Play button
    page.add(
        ft.Column(
            [
                ft.Container(
                    lyric_display,
                    padding=30,
                    bgcolor="#455a64",
                    border_radius=10,
                    height=160,
                    width=600,
                    alignment=ft.Alignment(0, 0)
                ),
                ft.ElevatedButton("Play", on_click=lambda _: pygame.mixer.music.play())
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )

ft.run(main)