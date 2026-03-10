import flet as ft
import yt_dlp
import os

def main(page: ft.Page):
    page.title = "Aesthetic Music Downloader"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # 1. Define Input and Output
    url_field = ft.TextField(label="Paste YouTube URL here", width=400)
    status_text = ft.Text("Ready to download...")

    # 2. Download Logic
    def download_audio(e):
        url = url_field.value
        if not url:
            status_text.value = "Please enter a URL!"
            page.update()
            return

        status_text.value = "Downloading..."
        page.update()

        try:
            # Setup yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'downloads/%(title)s.%(ext)s',
            }
            
            # Run download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            status_text.value = "Download complete!"
        except Exception as ex:
            status_text.value = f"Error: {ex}"
        
        page.update()

    # 3. Add to UI
    page.add(
        url_field,
        ft.ElevatedButton("Download MP3", on_click=download_audio),
        status_text
    )

ft.app(target=main)