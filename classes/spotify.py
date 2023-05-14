from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError

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
                self.__CLIENT_CREDENTIALS_MGR = SpotifyClientCredentials(
                    client_id=self.__CLIENT_ID, client_secret=self.__CLIENT_SECRET
                )
                self.__sp = spotipy.Spotify(
                    client_credentials_manager=self.__CLIENT_CREDENTIALS_MGR
                )
        except SpotifyOauthError:
            print("No se pudo autenticar con la API de Spotify. Por favor, verifique sus credenciales.")  # fmt: skip

    def get_audio_features(
        self,
        song_id: Union[str, List[str]],
        ) -> Dict:  # fmt: skip
        """
        Obtiene las características de audio de una canción de Spotify.

        Parameters:
            song_id Union[List[List[str]], str]: ID o ID's de la canción de Spotify.

        Returns:
            Diccionario con las características de audio de la canción.
        """

        if isinstance(song_id, str):
            # Si song_id es un string retornar resultado
            return self.__sp.audio_features(tracks=song_id)

        # Dividir la lista de canciones en sublistas de máximo 100 elementos
        sublists = [song_id[i : i + 100] for i in range(0, len(song_id), 100)]

        # Llamar a la función audio_features para cada sublista y concatenar las listas resultantes
        audio_features_list = [
            feature
            for sublist in sublists
            for feature in self.__sp.audio_features(tracks=sublist)
        ]

        return audio_features_list

    def get_playlist_info(
        self,
        playlist_id: Union[str, List[str]],
        user: str = None,
        fields: List[str] = None,
    ) -> Dict:
        """
        Obtiene información sobre una playlist de Spotify.

        Parameters:
            playlist_id (str): ID de la playlist de Spotify.
            user (str): Nombre de usuario del propietario de la playlist.
            fields (List[str]): Lista de campos de la playlist que se deben devolver.

        Returns:
            Diccionario con la información de la playlist solicitada.
        """
        return self.__sp.user_playlist(
            user=user, playlist_id=playlist_id, fields=fields
        )

    def get_playlist_data(self, playlist_id: str) -> None:
        """
        Recupera todos los tracks de una playlist de Spotify.

        Parameters:
            playlist_id (str): ID de la playlist de Spotify.

        Returns:
            Lista con todos los tracks de la playlist.
        """
        # Configurar el nombre de la playlist
        playlist_name = self.get_playlist_info(
            playlist_id=playlist_id, fields=["name"]
        )["name"]

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
        playlist_data = self.extract_playlist_data(
            playlist_id=playlist_id, raw_path=raw_data_path
        )

        return self.get_model_data(
            playlist_data=playlist_data, parquet_path=parquet_data_path
        )

    def extract_playlist_data(self, playlist_id: str, raw_path: str) -> List[Dict]:
        """
        Recupera todos los tracks de una playlist de Spotify.

        Parameters:
            playlist_id (str): ID de la playlist de Spotify.

        Returns:
            Lista con todos los tracks de la playlist.
        """

        # Configurar los parámetros de la consulta
        offset, limit = 0, 100
        playlist_data = []

        # Recuperar los tracks de la playlist en bloques de tamaño `limit`
        while True:
            playlist_tracks = self.__sp.playlist_tracks(
                playlist_id=playlist_id, offset=offset, limit=limit
            )

            # Agregar los tracks a la lista de resultados
            playlist_data += playlist_tracks["items"]
            offset += limit

            # Guardar la data en bruto en formato JSON
            raw_data_file_path_temp = f"{raw_path}/data_{offset}.json"
            dev.save_raw_json(
                json_path=raw_data_file_path_temp,
                json_dict=playlist_tracks
            )  # fmt: skip

            # Si no hay más tracks en la playlist, terminar el bucle
            if playlist_tracks["next"] is None:
                break

        return playlist_data

    def get_model_data(self, playlist_data: List[Dict], parquet_path: str) -> None:
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
        album_df = album_df.drop_duplicates(subset="album_id")
        artist_df = artist_df.drop_duplicates(subset="artist_id")
        song_df = song_df.drop_duplicates(subset="song_id")

        # Obteniendo las características de cada canción
        # que se encuentra en la playlist
        songs_features = self.get_audio_features(song_id=song_df["song_id"])
        songs_features_df = pd.DataFrame(songs_features)

        # Guardando archivos
        album_df.to_parquet(f"{parquet_path}/albums.parquet")
        artist_df.to_parquet(f"{parquet_path}/artists.parquet")
        song_df.to_parquet(f"{parquet_path}/songs.parquet")
        songs_features_df.to_parquet(f"{parquet_path}/songs_features.parquet")

        return
