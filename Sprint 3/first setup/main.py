# main.py
import flet as ft
from library import get_library_widget
from player import PlayerWidget

def main(page: ft.Page):
    page.title = "Audio Display - Player"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.window_width = 650
    page.window_height = 850
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # 1. Instantiate the Player Widget
    player_engine = PlayerWidget(page)

    # 2. Callback function when a track is clicked in the Library
    def on_select_song(artist, album, song):
        player_engine.load_track(artist, album, song)

    # 3. Instantiate the Library/Search Widget
    library_ui = get_library_widget(on_song_select=on_select_song)

    # 4. Add components to the page layout
    page.add(
        ft.Column([
            library_ui,          # Top Search & Track List (PDF Page 4)
            ft.Divider(color="#2A2A3D"),
            player_engine.get_widget() # Bottom Player Display (PDF Pages 1-3)
        ], spacing=15)
    )

if __name__ == "__main__":
    ft.run(main)