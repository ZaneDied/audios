# main.py
import flet as ft
from library import get_library_widget
from player import PlayerWidget

def main(page: ft.Page):
    page.title = "Music Player"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#000000"

    player_app = None

    def on_song_select(artist, album, song):
        if player_app:
            player_app.load_track(artist, album, song)

    browse_widget = get_library_widget(on_song_select)
    player_app = PlayerWidget(page, browse_widget=browse_widget)

    page.add(player_app.get_widget())

if __name__ == "__main__":
    ft.app(target=main)