from classes.spotify import SpotifyAPI

spotify = SpotifyAPI()


def extract_playlist_data(playlist_url: str) -> None:
    # Obteniendo ID del link de la Playlist
    ID = playlist_url.split("/")[-1].split("?")[0]

    # Datos de las canciones que tienen la playlist a buscar por ID
    spotify.get_playlist_data(playlist_id=ID)


if __name__ == "__main__":
    urls = [
        "https://open.spotify.com/playlist/1jRjHPZ1H4fX3LU81FkwWR?si=e5f0577b120a4c92",
        "https://open.spotify.com/playlist/1pN3ATrNrMf8lbf0TFV5m5?si=45a4bfcf11464421",
        "https://open.spotify.com/playlist/6PLBKNjA9IwsKZfi5mCj0v?si=78a69210bb1b4717",
        "https://open.spotify.com/playlist/0WcaV6uVrFEUoPMqQUsHVn?si=d42c12fdfee24ccf",
        "https://open.spotify.com/playlist/7n6ku72zf9yBZuEvqQRgQg?si=b66a59a12333485e",
    ]

    for url in urls:
        extract_playlist_data(playlist_url=url)
