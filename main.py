from classes import dev
from classes.spotify_v2 import SpotifyAPI

spotify = SpotifyAPI()


if __name__ == "__main__":
    # URL's de diversas Playlist a ejecutar
    urls = [
        "https://open.spotify.com/playlist/1jRjHPZ1H4fX3LU81FkwWR?si=e5f0577b120a4c92",
        "https://open.spotify.com/playlist/1pN3ATrNrMf8lbf0TFV5m5?si=45a4bfcf11464421",
        "https://open.spotify.com/playlist/6PLBKNjA9IwsKZfi5mCj0v?si=78a69210bb1b4717",
        "https://open.spotify.com/playlist/0WcaV6uVrFEUoPMqQUsHVn?si=d42c12fdfee24ccf",
        "https://open.spotify.com/playlist/7n6ku72zf9yBZuEvqQRgQg?si=b66a59a12333485e",
    ]

    for url in urls:
        # Datos de las canciones que tienen la playlist a buscar por ID
        playlist_id = dev.get_id_playlist(playlist_url=url)

        # Extraer data de Playlist
        spotify.playlist_data(playlist_id=playlist_id)
