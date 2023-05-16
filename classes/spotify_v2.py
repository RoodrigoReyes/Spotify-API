from datetime import datetime
from typing import Dict, List, Union, Optional, Any

import pandas as pd
import requests

from classes import dev
from classes.env import EnvAttr

TODAY = datetime.today().strftime("%Y-%m-%d")


class SpotifyAPI:
    def __init__(self):
        try:
            # Cargar credenciales desde variables de entorno o un archivo
            credentials = EnvAttr(json_path="credentials/secret.json")

            # Obtener credenciales de Spotify
            spotify_creds = credentials.attr.get("Spotify", {})
            self.__CLIENT_ID = spotify_creds.get("CLIENT_ID")
            self.__CLIENT_SECRET = spotify_creds.get("CLIENT_SECRET")

            # Crear un objeto para proporcionar autorización para acceder a los datos
            if self.__CLIENT_ID and self.__CLIENT_SECRET:
                self.__auth_response = requests.post(
                    "https://accounts.spotify.com/api/token",
                    {
                        "grant_type": "client_credentials",
                        "client_id": self.__CLIENT_ID,
                        "client_secret": self.__CLIENT_SECRET,
                    },
                )

                self.__auth_response_data = self.__auth_response.json()
                self.__access_token = self.__auth_response_data["access_token"]
                self.__headers = {"Authorization": f"Bearer {self.__access_token}"}

        except requests.exceptions.RequestException as e:
            raise Exception("No se pudo autenticar con la API de Spotify. Por favor, verifique sus credenciales.")  # fmt: skip

    def make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict:
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

        if response.status_code != 200:
            raise Exception("Error al recuperar los datos")
        return response.json()

    def track_info(self, song_id: str):
        # Get requests para obtener data
        response = self.make_request(url=f"https://api.spotify.com/v1/tracks/{song_id}")

        return response

    def playlist_info(self, playlist_id: str):
        # Get requests para obtener data
        response = self.make_request(
            url=f"https://api.spotify.com/v1/playlists/{playlist_id}"
        )

        return response

    def playlist_tracks(self, playlist_id: str, raw_path: str):
        # Configurar los parámetros de la consulta
        offset, limit = 0, 100
        playlist_data = []

        while True:
            params = {"offset": offset, "limit": limit}

            response = self.make_request(
                url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                params=params,
            )

            # Agregar los tracks a la lista de resultados
            playlist_data += response["items"]
            offset += limit

            # Guardar la data en bruto en formato JSON
            raw_data_file_path_temp = f"{raw_path}/data_{offset}.json"
            dev.save_raw_json(
                json_path=raw_data_file_path_temp,
                json_dict=response
            )  # fmt: skip

            # Si no hay más tracks en la playlist, terminar el bucle
            if response["next"] is None:
                break

        return playlist_data

    def audio_feature(self, song_id: Union[str, List[str]]) -> Dict:
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
            return self.make_request(url)

        elif isinstance(song_id, pd.Series) and len(song_id) <= 100:
            # Obtener características de audio para varias canciones (hasta 100)
            url = f"https://api.spotify.com/v1/audio-features?ids={','.join(song_id)}"
            return self.make_request(url)["audio_features"]

        elif isinstance(song_id, pd.Series) and len(song_id) > 100:
            # Obtener características de audio para varias canciones (más de 100)
            # Dividir la lista de IDs en sub-listas de máximo 100 IDs
            sublists = [song_id[i : i + 100] for i in range(0, len(song_id), 100)]

            # Obtener características de audio para cada sub-lista de IDs
            audio_features_list = [
                feature
                for sublist in sublists
                for feature in self.make_request(
                    f"https://api.spotify.com/v1/audio-features?ids={','.join(sublist)}"
                )["audio_features"]
            ]

            return audio_features_list

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
        album_df = pd.DataFrame.from_dict(dev.album_data(playlist_data))
        artist_df = pd.DataFrame.from_dict(dev.artist_data(playlist_data))
        song_df = pd.DataFrame.from_dict(dev.songs_data(playlist_data))

        # Eliminando duplicados por id
        """album_df = album_df.drop_duplicates(subset="album_id")
        artist_df = artist_df.drop_duplicates(subset="artist_id")
        song_df = song_df.drop_duplicates(subset="song_id")"""

        # Obteniendo las características de cada canción
        # que se encuentra en la playlist
        songs_features = self.audio_feature(song_id=song_df["song_id"])
        songs_features_df = pd.DataFrame(songs_features)

        # Guardando archivos
        album_df.to_parquet(f"{parquet_path}/albums.parquet")
        artist_df.to_parquet(f"{parquet_path}/artists.parquet")
        song_df.to_parquet(f"{parquet_path}/songs.parquet")
        songs_features_df.to_parquet(f"{parquet_path}/songs_features.parquet")

        return

    def playlist_data(self, playlist_id: str) -> None:
        """
        Recupera todos los tracks de una playlist de Spotify.

        Parameters:
            playlist_id (str): ID de la playlist de Spotify.

        Returns:
            Lista con todos los tracks de la playlist.
        """
        # Obtener el nombre de la playlist
        playlist_name = self.playlist_info(playlist_id=playlist_id)["name"]

        # Crear el directorio principal y los subdirectorios
        today_directory_path = dev.create_directory(directory_path="api_data",
                                                    subdirectory_name=TODAY)  # fmt: skip

        # Crear directorios para identificar el dia de ejecucion
        raw_data_today_path = dev.create_directory(directory_path=today_directory_path,
                                                   subdirectory_name=playlist_name)  # fmt: skip

        parquet_data_today_path = dev.create_directory(directory_path=today_directory_path,
                                                       subdirectory_name=playlist_name)  # fmt: skip

        # Crear un subdirectorio con la fecha actual
        raw_data_path = dev.create_directory(directory_path=raw_data_today_path,
                                             subdirectory_name="raw_data")  # fmt: skip

        parquet_data_path = dev.create_directory(directory_path=parquet_data_today_path,
                                                 subdirectory_name="parquet_data")  # fmt: skip

        # Configurar los parámetros de la consulta
        playlist_data = self.playlist_tracks(
            playlist_id=playlist_id, raw_path=raw_data_path
        )

        return self.model_data(
            playlist_data=playlist_data, parquet_path=parquet_data_path
        )
