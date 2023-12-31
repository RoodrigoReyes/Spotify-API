from tqdm import tqdm

from classes import utils
from classes.spotify import SpotifyAPI

spotify = SpotifyAPI()


if __name__ == "__main__":
    # URL's de diversas Playlist a ejecutar
    current_user_playlist_data = utils.user_current_playlist_data(
        current_playlists=spotify.user_current_playlists()
    )

    for row in tqdm(
        current_user_playlist_data, desc="Extracting Spotify data from API", ncols=120
    ):
        # Datos de las canciones que tienen la playlist a buscar por ID
        playlist_id = row["playlist_id"]
        playlist_name = row["playlist_name"].strip().ljust(28)

        # Extraer data de Playlist
        spotify.playlist_data(playlist_id=playlist_id)

        # print(f"{playlist_name} extraida con éxito!")
