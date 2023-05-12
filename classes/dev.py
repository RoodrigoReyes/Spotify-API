import json
from pathlib import Path
from typing import Dict, List


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
        subdirectory_path = f"{directory_path}/{subdirectory_name}"
        Path(subdirectory_path).mkdir(parents=True, exist_ok=True)

        return subdirectory_path

    return directory_path


def save_raw_json(json_path: str, json_dict: Dict) -> None:
    # Guardar la data en bruto en formato JSON
    with open(json_path, "w") as fp:
        json.dump(json_dict, fp, indent=4)


def album_data(playlist_data: List[str]) -> List[Dict]:
    return [
        {
            "album_id": row["track"]["album"]["id"],
            "name": row["track"]["album"]["name"],
            "release_date": row["track"]["album"]["release_date"],
            "total_tracks": row["track"]["album"]["total_tracks"],
            "url": row["track"]["album"]["external_urls"]["spotify"],
        }
        for row in playlist_data
        if row["track"] is not None
    ]


def artist_data(playlist_data: List[str]) -> List[Dict]:
    return [
        {
            "artist_id": artist["id"],
            "artist_name": artist["name"],
            "artist_type": artist["type"],
            "external_url": artist["external_urls"]["spotify"],
        }
        for row in playlist_data
        for key, value in row.items()
        if key == "track" and value is not None
        for artist in value["artists"]
    ]


def songs_data(playlist_data: List[str]) -> List[Dict]:
    return [
        {
            "song_id": row["track"]["id"],
            "song_name": row["track"]["name"],
            "duration_ms": row["track"]["duration_ms"],
            "url": row["track"]["external_urls"]["spotify"],
            "popularity": row["track"]["popularity"],
            "explicit": row["track"]["explicit"],
            "song_added": row["added_at"],
            "album_id": row["track"]["album"]["id"],
            "artist_id": row["track"]["album"]["artists"][0]["id"],
        }
        for row in playlist_data
        if row["track"] is not None
    ]
