from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

import pandas as pd
import requests
import spotipy.util as util

from classes import utils
from classes.env import EnvAttr

YEAR_MONTH_DAY = datetime.today().strftime("%Y-%m-%d")
MONTH_YEAR = datetime.today().strftime("%B, %Y")


class SpotifyAPI:
    def __init__(self):
        try:
            # Cargar credenciales desde variables de entorno o un archivo
            credentials = EnvAttr(json_path="config/secret.json")

            # Obtener credenciales de Spotify
            spotify_creds = credentials.attr.get("Spotify", {})
            self.__CLIENT_ID = spotify_creds.get("CLIENT_ID")
            self.__CLIENT_SECRET = spotify_creds.get("CLIENT_SECRET")
            self.__USERNAME = spotify_creds.get("USERNAME")
            self.__REDIRECT_URI = spotify_creds.get("REDIRECT_URI")
            self.__scope = spotify_creds.get("SCOPE")

            # Crear un objeto para proporcionar autorización para acceder a los datos
            if self.__CLIENT_ID and self.__CLIENT_SECRET:
                self.__access_token = util.prompt_for_user_token(
                    username=self.__USERNAME,
                    client_id=self.__CLIENT_ID,
                    client_secret=self.__CLIENT_SECRET,
                    redirect_uri=self.__REDIRECT_URI,
                    scope=self.__scope,
                )
                self.__headers = {
                    "Authorization": f"Bearer {self.__access_token}",
                    "Content-Type": "application/json",
                }

        except requests.exceptions.RequestException as e:
            raise Exception(
                "No se pudo autenticar con la API de Spotify. Por favor, verifique sus credenciales."
            )

    def get_requests(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Realiza una solicitud HTTP GET a la URL especificada con parámetros de consulta opcionales.

        Parámetros:
            url (str): La URL a la cual se realiza la solicitud.
            params (Optional[Dict[str, Any]]): Parámetros de consulta opcionales para la solicitud.

        Retorna:
            Dict: La respuesta JSON de la solicitud.

        Lanza:
            Exception: Si la solicitud falla o el código de estado de la respuesta no es 200.
        """
        if not params:
            # Realizar solicitud GET sin parámetros
            response = requests.get(url, headers=self.__headers)
        else:
            # Realizar solicitud GET con parámetros
            response = requests.get(url, headers=self.__headers, params=params)

        if response.status_code not in (200, 201):
            raise Exception("Error al recuperar los datos")
        return response.json()

    def post_requests(self, url: str, data: Dict) -> Dict:
        response = requests.post(url, headers=self.__headers, json=data)

        if response.status_code not in (200, 201):
            raise Exception("Error creating playlist")

        return response.json()

    def put_requests(self, url: str) -> Dict:
        response = requests.put(url, headers=self.__headers)

        if response.status_code not in (200, 201):
            raise Exception("Error creating playlist")

        return response.json()

    def user_info(self) -> Dict:
        """
        Obtiene informacion del usuario de la cuenta

        Returns:
           response (Dict): La respuesta JSON con la data del usuario.
        """
        response = self.get_requests(url="https://api.spotify.com/v1/me")

        return response

    def get_tops_user(
        self,
        type: str,
        time_range: Literal["short_term", "medium_term", "long_term"] = "long_term",
        limit: int = 50,
        offset: int = 0,
    ) -> Dict:
        """
        Get the current user's top tracks based on calculated affinity over the last several years.

        The `time_range` parameter can be one of the following values:

        * `short_term`: The last 4 weeks
        * `medium_term`: The last 6 months
        * `long_term`: The last year

        Parameters:
            time_range (str): The time range for the top tracks.
            limit (int): The maximum number of tracks to return. Default: 50.
            offset (int): The index of the first track to return. Default: 0 (the first track).

        Returns:
            Dict: The JSON response from the request.

        Raises:
            Exception: If the request fails or the response status code is not 200.
        """

        # Configurar los parámetros de la consulta
        top = []
        for offset in range(0, 50):
            params = {
                "time_range": time_range,
                "limit": limit,
                "offset": offset,
            }

            response = self.get_requests(
                url=f"https://api.spotify.com/v1/me/top/{type}",
                params=params,
            )

            # Agregar los tracks a la lista de resultados
            top += response["items"]

        return top

    def create_playlist(self, name: str, description: str = "", public: bool = False):
        """
        Creates a new playlist for the specified user with the given name and description.

        Parameters:
            name (str): The name of the new playlist.
            description (str): An optional description of the new playlist.
            public (bool): A boolean value indicating whether the new playlist should be public or not.

        Returns:
            dict: The JSON response from the Spotify API.

        Raises:
            Exception: If the request fails or the response status code is not 200.
        """

        user_id = self.user_info()["id"]
        url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        data = {
            "name": f"{name} {MONTH_YEAR}",
            "description": description,
            "public": public,
        }

        response = self.post_requests(url=url, data=data)

        return response["id"]

    def add_tracks_to_playlist(self, playlist_id: str, track_uris: pd.Series) -> Dict:
        """
        Adds tracks to a playlist in Spotify.

        Parameters:
            playlist_id (str): The Spotify ID of the playlist to which to add tracks.
            track_uris (List[str]): A list of Spotify URIs of the tracks to add to the playlist.
            position (Optional[int]): The position in the playlist where to insert the tracks.

        Returns:
            dict: The JSON response from the Spotify API.

        Raises:
            Exception: If the request fails or the response status code is not 200.
        """

        if isinstance(track_uris, pd.Series) and len(track_uris) <= 100:
            songs_ids = ",".join(
                ["spotify:track:" + track_id for track_id in track_uris]
            )
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={songs_ids}"
            self.put_requests(url)

            return f"Canciones añadidas a playlist"

        elif isinstance(track_uris, pd.Series) and len(track_uris) > 100:
            # Obtener características de audio para varias canciones (más de 100)
            # Dividir la lista de IDs en sub-listas de máximo 100 IDs
            track_songs_ids = ["spotify:track:" + track_id for track_id in track_uris]
            sublists = [
                track_songs_ids[i : i + 100]
                for i in range(0, len(track_songs_ids), 100)
            ]

            print("Cantida de registro de 100 a agregar:", len(sublists))
            for index, sublist in enumerate(sublists):
                print(index, "->", len(sublist))
                songs_ids = ",".join(sublist)
                url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={songs_ids}"
                response = self.put_requests(url=url)

                print(response)
            return f"Canciones añadidas a playlist"

        return "Error en la adicion de canciones"

    def track_search(self, song_name: str, artist_name: Union[str, Any] = None):
        # Set the API endpoint URL
        url = "https://api.spotify.com/v1/search"

        if song_name and artist_name:
            # Set the query parameters for searching tracks
            params = {"q": f"{song_name} artist:{artist_name}", "type": "track"}

            # Set the Authorization header with the access token
            # Send a GET request to the API endpoint
            response = self.get_requests(url=url, params=params)

            # Parse the JSON response and extract the relevant information about the track(s)
            tracks = response["tracks"]["items"]
            if len(tracks) > 0:
                track = tracks[0]  # Get the first track in the search results
                return track["id"]
            else:
                # Set the query parameters for searching tracks
                params = {"q": f"{song_name}", "type": "track"}

                # Set the Authorization header with the access token
                # Send a GET request to the API endpoint
                response = self.get_requests(url=url, params=params)

                # Parse the JSON response and extract the relevant information about the track(s)
                tracks = response["tracks"]["items"]
                if len(tracks) > 0:
                    track = tracks[0]  # Get the first track in the search results
                    return track["id"]
                else:
                    return None

    def playlist_info(self, playlist_id: str):
        # Get requests para obtener data
        response = self.get_requests(
            url=f"https://api.spotify.com/v1/playlists/{playlist_id}"
        )

        return response

    def playlist_tracks(self, playlist_id: str, raw_path: str):
        # Configurar los parámetros de la consulta
        offset, limit = 0, 100
        playlist_data = []

        while True:
            params = {"offset": offset, "limit": limit}

            response = self.get_requests(
                url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                params=params,
            )

            # Agregar los tracks a la lista de resultados
            playlist_data += response["items"]
            offset += limit

            # Guardar la data en bruto en formato JSON
            raw_data_file_path_temp = f"{raw_path}/data_{offset}.json"
            utils.save_raw_json(
                json_path=raw_data_file_path_temp,
                json_dict=response
            )  # fmt: skip

            # Si no hay más tracks en la playlist, terminar el bucle
            if response["next"] is None:
                break

        return playlist_data

    def user_current_playlists(self) -> List[Dict]:
        url = "https://api.spotify.com/v1/me/playlists"
        response = self.get_requests(url=url)["items"]

        return response

    def playlist_data(self, playlist_id: str) -> None:
        """
        Recupera todos los tracks de una playlist de Spotify.

        Parameters:
            playlist_id (str): ID de la playlist de Spotify.

        Returns:
            Lista con todos los tracks de la playlist.
        """
        # Obtener el nombre de la playlist
        self.playlist_name = self.playlist_info(playlist_id=playlist_id)["name"]

        # Crear el directorio principal y los subdirectorios
        today_directory_path = utils.create_directory(directory_path="api_data",
                                                    subdirectory_name=YEAR_MONTH_DAY)  # fmt: skip

        # Crear directorios para identificar el dia de ejecucion
        raw_data_today_path = utils.create_directory(directory_path=today_directory_path,
                                                   subdirectory_name=self.playlist_name)  # fmt: skip

        parquet_data_today_path = utils.create_directory(directory_path=today_directory_path,
                                                       subdirectory_name=self.playlist_name)  # fmt: skip

        # Crear un subdirectorio con la fecha actual
        raw_data_path = utils.create_directory(directory_path=raw_data_today_path,
                                             subdirectory_name="raw_data")  # fmt: skip

        parquet_data_path = utils.create_directory(directory_path=parquet_data_today_path,
                                                 subdirectory_name="parquet_data")  # fmt: skip

        # Configurar los parámetros de la consulta
        playlist_data = self.playlist_tracks(
            playlist_id=playlist_id, raw_path=raw_data_path
        )

        self.model_data(playlist_data=playlist_data, parquet_path=parquet_data_path)

        return playlist_data

    def audio_feature(self, song_id: Union[str, pd.Series]) -> Dict:
        """
        Obtiene las características de audio de una o varias canciones de Spotify.

        Parámetros:
            - song_id (Union[str, List[str]]): ID o lista de IDs de la canción(es) de Spotify.

        Retorna:
            - Dict: Diccionario con las características de audio de la canción (o canciones).
        """

        if isinstance(song_id, str):
            # Obtener características de audio para una sola canción
            url = f"https://api.spotify.com/v1/audio-features/{song_id}"
            audio_features = self.get_requests(url)

        elif isinstance(song_id, pd.Series) and len(song_id) <= 100:
            # Obtener características de audio para varias canciones (hasta 100)
            url = f"https://api.spotify.com/v1/audio-features?ids={','.join(song_id)}"
            audio_features = self.get_requests(url)["audio_features"]

        elif isinstance(song_id, pd.Series) and len(song_id) > 100:
            # Obtener características de audio para varias canciones (más de 100)
            # Dividir la lista de IDs en sub-listas de máximo 100 IDs
            sublists = [song_id[i : i + 100] for i in range(0, len(song_id), 100)]

            # Obtener características de audio para cada sub-lista de IDs
            audio_features = [
                feature
                for sublist in sublists
                for feature in self.get_requests(
                    f"https://api.spotify.com/v1/audio-features?ids={','.join(sublist)}"
                )["audio_features"]
                if feature is not None
            ]

        return audio_features

    def model_data(self, playlist_data: List[Dict], parquet_path: str) -> None:
        """
        Procesa los datos de la playlist y guarda la información de los álbumes, artistas,
        canciones y sus características en archivos parquet.

        Parameters:
            playlist_data (List[Dict]): Lista de diccionarios con la información de los tracks de la playlist.
            parquet_path (str): Ruta del directorio donde se guardarán los archivos parquet.

        Returns:
            None
        """

        # Obteniendo informacion de los albumes, artistas y canciones
        # que estan en la playlist
        album_df = pd.DataFrame.from_dict(utils.album_data(playlist_data))
        artist_df = pd.DataFrame.from_dict(utils.artist_data(playlist_data))
        song_df = pd.DataFrame.from_dict(utils.songs_data(playlist_data))

        # Eliminando duplicados por id
        album_df = album_df.drop_duplicates(subset="album_id")
        artist_df = artist_df.drop_duplicates(subset="artist_id")
        song_df = song_df.drop_duplicates(subset="song_id")

        # Obteniendo las características de cada canción
        # que se encuentra en la playlist
        songs_features = self.audio_feature(song_id=song_df["song_id"])
        songs_features_df = pd.DataFrame(songs_features)
        songs_features_df = songs_features_df.rename(columns={"id": "song_id"})

        # Uniendo los datos para tener un solo archivo consolidado
        df_1 = pd.merge(left=song_df, right=songs_features_df, on="song_id")
        df_2 = pd.merge(left=df_1, right=album_df, on="album_id")
        df_merge_data = pd.merge(left=df_2, right=artist_df, on="artist_id")

        # Definiendo paths para guardando archivos
        album_path = f"{parquet_path}/albums.parquet"
        artist_path = f"{parquet_path}/artists.parquet"
        song_path = f"{parquet_path}/songs.parquet"
        songs_features_path = f"{parquet_path}/songs_features.parquet"
        df_merge_data_path = f"{parquet_path}/merge_data.parquet"

        album_df.to_parquet(album_path)
        artist_df.to_parquet(artist_path)
        song_df.to_parquet(song_path)
        songs_features_df.to_parquet(songs_features_path)
        df_merge_data.to_parquet(df_merge_data_path)

        return True
