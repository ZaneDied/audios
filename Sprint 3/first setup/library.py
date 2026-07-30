# library.py
import flet as ft
import os

def get_library_widget(on_song_select):
    """
    Scans MusicLibrary directory and returns the Search/Library UI component.
    """
    base_dir = os.path.join(os.getcwd(), "MusicLibrary")

    search_bar = ft.TextField(
        hint_text="Search something or download",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        bgcolor="#1E1E2E",
        border_radius=12,
        border_color="#2A2A3D",
        focused_border_color="#6C5CE7",
        content_padding=15,
        expand=True
    )

    # 1. Column just handles scrolling and alignment
    song_list_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)

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
                                
                                if filter_query.lower() in full_title.lower():
                                    found_any = True
                                    song_item = ft.Container(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, color="#6C5CE7", size=20),
                                            ft.Column([
                                                ft.Text(song_name, size=14, weight="bold", color="white"),
                                                ft.Text(f"{artist} • {album}", size=11, color="#B3B3B3")
                                            ], spacing=2, expand=True)
                                        ], alignment=ft.MainAxisAlignment.START),
                                        padding=10,
                                        bgcolor="#181824",
                                        border_radius=8,
                                        on_click=lambda e, a=artist, al=album, s=song_name: on_song_select(a, al, s),
                                        ink=True
                                    )
                                    song_list_column.controls.append(song_item)

        if not found_any:
            song_list_column.controls.append(
                ft.Text("No matching tracks found", color="#8E8E93", size=13)
            )

    search_bar.on_change = lambda e: scan_music_library(e.control.value)
    scan_music_library()

    # 2. Wrap song_list_column inside a Container with height=180 to constrain height
    song_list_container = ft.Container(
        content=song_list_column,
        height=180
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([search_bar]),
            ft.Text("Library / Track List", size=12, weight="bold", color="#8E8E93"),
            song_list_container  # <-- Used container here
        ], spacing=10),
        padding=15,
        bgcolor="#121218",
        border_radius=16,
        border=ft.border.all(1, "#2A2A3D")
    )