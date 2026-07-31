# library.py
import flet as ft
import os
import shutil
import asyncio
from request import download_youtube_track
ft.Icons = ft.icons
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.join(SCRIPT_DIR, "MusicLibrary")

def get_library_widget(on_song_select):
    """
    Scans MusicLibrary directory, handles downloads, and allows track deletion.
    """
    search_input = ft.TextField(
        hint_text="Search local songs OR paste YouTube link...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        bgcolor="#1E1E2E",
        border_radius=12,
        border_color="#2A2A3D",
        focused_border_color="#6C5CE7",
        content_padding=15,
        expand=True
    )

    status_text = ft.Text("Ready", size=12, color="#8E8E93")
    loading_progress = ft.ProgressRing(width=16, height=16, stroke_width=2, visible=False)
    song_list_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)

    def delete_song(artist, song_folder_name):
        """Deletes the song folder from MusicLibrary."""
        target_path = os.path.join(base_dir, artist, song_folder_name)
        if os.path.exists(target_path):
            try:
                shutil.rmtree(target_path)
                
                # Clean up empty artist directory if empty
                artist_dir = os.path.join(base_dir, artist)
                if os.path.exists(artist_dir) and not os.listdir(artist_dir):
                    os.rmdir(artist_dir)
                    
                status_text.value = f"Deleted '{song_folder_name}'"
                status_text.color = "#FF7675"
            except Exception as err:
                status_text.value = f"Error deleting: {err}"
                status_text.color = "#FF7675"
        
        scan_music_library(search_input.value or "")
        # Only update controls if they are currently on the page
        if status_text.page:
            status_text.update()
            song_list_column.update()

    def scan_music_library(filter_query=""):
        song_list_column.controls.clear()

        if not os.path.exists(base_dir):
            song_list_column.controls.append(
                ft.Text("MusicLibrary directory not found.", color="#8E8E93", size=12)
            )
            return

        found_any = False

        for artist in os.listdir(base_dir):
            artist_path = os.path.join(base_dir, artist)
            if os.path.isdir(artist_path):
                for album in os.listdir(artist_path):
                    album_path = os.path.join(artist_path, album)
                    if os.path.isdir(album_path):
                        for file in os.listdir(album_path):
                            if file.endswith(".mp3"):
                                song_name = file[:-4]
                                full_title = f"{song_name} - {artist}"

                                if filter_query.lower() in full_title.lower() or "http" in filter_query:
                                    found_any = True

                                    # Song Item Row
                                    song_item = ft.Container(
                                        content=ft.Row([
                                            # Left: Click to Play
                                            ft.Container(
                                                content=ft.Row([
                                                    ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, color="#6C5CE7", size=20),
                                                    ft.Column([
                                                        ft.Text(song_name, size=13, weight="bold", color="white"),
                                                        ft.Text(f"{artist}", size=11, color="#B3B3B3")
                                                    ], spacing=2)
                                                ]),
                                                expand=True,
                                                on_click=lambda e, a=artist, al=album, s=song_name: on_song_select(a, al, s),
                                            ),
                                            
                                            # Right: Delete Track
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINED,
                                                icon_size=18,
                                                icon_color="#FF7675",
                                                tooltip="Delete track",
                                                on_click=lambda e, a=artist, al=album: delete_song(a, al)
                                            )
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                        padding=ft.padding.only(left=10, right=5, top=5, bottom=5),
                                        bgcolor="#181824",
                                        border_radius=8,
                                        ink=True
                                    )
                                    song_list_column.controls.append(song_item)

        if not found_any and "http" not in filter_query:
            song_list_column.controls.append(
                ft.Text("No matching tracks found", color="#8E8E93", size=13)
            )

    async def handle_download(e):
        url = search_input.value.strip()
        if not url:
            status_text.value = "Enter a YouTube link or search query first!"
            status_text.color = "#FF7675"
            status_text.update()
            return

        if "youtube.com" in url or "youtu.be" in url:
            loading_progress.visible = True
            status_text.value = "Downloading track..."
            status_text.color = "#6C5CE7"
            search_input.disabled = True
            status_text.update()
            loading_progress.update()
            search_input.update()

            try:
                artist, title = await asyncio.to_thread(download_youtube_track, url)
                status_text.value = f"Downloaded: {title}!"
                status_text.color = "#55E6C1"
                search_input.value = ""

                scan_music_library()
                on_song_select(artist, title, title)

            except Exception as err:
                status_text.value = f"Error: {err}"
                status_text.color = "#FF7675"

            finally:
                loading_progress.visible = False
                search_input.disabled = False
                loading_progress.update()
                search_input.update()
                status_text.update()
                song_list_column.update()

    search_input.on_change = lambda e: (scan_music_library(e.control.value), song_list_column.update())
    
    # Perform initial directory scan without triggering .update() call
    scan_music_library()

    download_button = ft.ElevatedButton(
        "Download",
        icon=ft.Icons.DOWNLOAD_ROUNDED,
        bgcolor="#6C5CE7",
        color="white",
        on_click=handle_download
    )

    song_list_container = ft.Container(
        content=song_list_column,
        height=180
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([search_input, download_button]),
            ft.Row([loading_progress, status_text], spacing=10),
            ft.Text("Library / Track List", size=12, weight="bold", color="#8E8E93"),
            song_list_container
        ], spacing=10),
        padding=15,
        bgcolor="#121218",
        border_radius=16,
        border=ft.border.all(1, "#2A2A3D")
    )