import json
import os
import re
from pathlib import Path
from typing import Dict, List


def check_date():
    """
    Solicita al usuario que ingrese una fecha en formato YYYY-MM-DD utilizando regex
    hasta que se ingrese una fecha válida.

    Returns:
        fecha (str): Una fecha en formato YYYY-MM-DD
    """

    while True:
        fecha = input("Ingrese una fecha en formato YYYY-MM-DD: ")

        # Verificar si la fecha cumple con el formato YYYY-MM-DD utilizando regex

        patron = re.compile("^\d{4}-\d{2}-\d{2}$")

        if patron.match(fecha):
            return fecha

        else:
            print(
                "La fecha ingresada no cumple con el formato YYYY-MM-DD. Intente nuevamente."
            )


def get_id_playlist(playlist_url: str) -> str:
    """
    Obtener ID de la Playlist a traves de su url
    Parameters:
        playlist_url (str): Url de acceso a la Playlist.

    Returns:
        id (str): Id de la Playlist.
    """

    # Obteniendo ID del link de la Playlist

    id = playlist_url.split("/")[-1].split("?")[0]

    return id


def create_directory(directory_path: str, subdirectory_name: str = None) -> str:
    """
    Crea un directorio y un subdirectorio dentro de él si se especifica.

    Parameters:
        directory_path (str): Ruta del directorio principal.
        subdirectory_name (str): Nombre del subdirectorio. Si no se especifica, no se crea un subdirectorio.

    Returns:
        La ruta del subdirectorio creado si se especificó un nombre para el subdirectorio. De lo contrario, elve la ruta del directorio principal.

    """

    # Crea el directorio principal
    Path(directory_path).mkdir(parents=True, exist_ok=True)

    # Si se especificó un nombre para el subdirectorio, crea el subdirectorio
    if subdirectory_name:
        subdirectory_path = os.path.join(directory_path, subdirectory_name)

        Path(subdirectory_path).mkdir(parents=True, exist_ok=True)

        return subdirectory_path

    return directory_path


def save_raw_json(json_path: str, json_dict: Dict) -> None:
    """
    Guarda un diccionario como archivo JSON en la ruta especificada.

    Parameters:
        json_path (str): Ruta del archivo JSON a guardar.
        json_dict (Dict): Diccionario con los datos a guardar.


    Returns:
        None
    """

    with open(json_path, "w") as fp:
        json.dump(json_dict, fp, indent=4)


def album_data(playlist_data: List[str]) -> List[Dict]:
    """
    Toma una lista de datos de una playlist de Spotify y devuelve una lista de
    diccionarios con información del álbum correspondiente a cada canción.

    Parameters:
        playlist_data (List[str]): Lista de diccionarios con datos de una playlist de Spotify

    Returns:
        albums_data (List[Dict]): Lista de diccionarios con información del álbum de cada canción.
    """

    albums_data = [
        {
            "album_id": row["track"]["album"]["id"],
            "album_name": row["track"]["album"]["name"],
            "album_release_date": row["track"]["album"]["release_date"],
            "album_total_tracks": row["track"]["album"]["total_tracks"],
            "album_url": row["track"]["album"]["external_urls"]["spotify"],
        }
        for row in playlist_data
        if row["track"] is not None
    ]

    return albums_data


def artist_data(playlist_data: List[str]) -> List[Dict]:
    """
    Toma una lista de datos de una playlist de Spotify y devuelve una lista de
    diccionarios con información del artista correspondiente a cada canción.

    Parameters:
        playlist_data (List[str]): Lista de diccionarios con datos de una playlist de Spotify

    Returns:
        artist_data (List[Dict]): Lista de diccionarios con información del artista de cada canción.
    """

    artist_data = [
        {
            "artist_id": artist["id"],
            "artist_name": artist["name"],
            "artist_type": artist["type"],
            "artist_external_url": artist["external_urls"]["spotify"],
        }
        for row in playlist_data
        for key, value in row.items()
        if key == "track" and value is not None
        for artist in value["artists"]
    ]

    return artist_data


def songs_data(playlist_data: List[str]) -> List[Dict]:
    """
    Toma una lista de datos de una playlist de Spotify y devuelve una lista de
    diccionarios con información de cada canción.

    Parameters:
        playlist_data (list): Lista de diccionarios con datos de una playlist de Spotify

    Returns:
        songs_data (list): Lista de diccionarios con información de cada canción.
    """

    songs_data = [
        {
            "song_id": row["track"]["id"],
            "song_name": row["track"]["name"],
            "song_duration_ms": row["track"]["duration_ms"],
            "song_url": row["track"]["external_urls"]["spotify"],
            "song_popularity": row["track"]["popularity"],
            "song_explicit": row["track"]["explicit"],
            "song_added": row["added_at"],
            "album_id": row["track"]["album"]["id"],
            "artist_id": row["track"]["album"]["artists"][0]["id"],
        }
        for row in playlist_data
        if row["track"] is not None
    ]

    return songs_data


def user_current_playlist_data(current_playlists: List[Dict]) -> List[Dict]:
    """
    Toma una lista de diccionarios de las playlist de Spotify del usuario
    devolviendo una lista de diccionarios con información del mismo.

    Parameters:
        playlist_data (List[str]): Lista de diccionarios con datos de una playlist de Spotify

    Returns:
        albums_data (List[Dict]): Lista de diccionarios con información del álbum de cada canción.
    """

    playlists_data = [
        {
            "playlist_id": row["id"],
            "playlist_name": row["name"],
        }
        for row in current_playlists
    ]

    return playlists_data


def user_current_playlist_get_id(playlists, playlist_name):
    """
    Función para obtener el ID de una lista de reproducción (playlist) dada su nombre.

    Args:
    playlists (list): Una lista de diccionarios que representan las listas de reproducción.
                      Cada diccionario debe tener las claves 'playlist_id' y 'playlist_name'.
    playlist_name (str): El nombre de la lista de reproducción cuyo ID queremos obtener.

    Returns:
    str: El ID de la lista de reproducción si se encuentra el nombre dado, o None si no se encuentra.

    """

    # Recorre la lista de listas de reproducción
    for playlist in playlists:
        # Verifica si el nombre de la lista de reproducción actual coincide con el dado
        if playlist["playlist_name"] == playlist_name:
            # Si es así, devuelve el ID de la lista de reproducción
            return playlist["playlist_id"]

    # Si se recorrió toda la lista y no se encontró el nombre de la lista de reproducción, se devuelve None
    return None
