# API de Spotify

Este proyecto consiste en un módulo de Python que proporciona una interfaz simplificada para la API web de Spotify, lo que permite la recuperación de varios datos sobre canciones, artistas, álbumes y listas de reproducción. La clase `SpotifyAPI` proporciona métodos para recuperar características de audio e información de listas de reproducción, así como todas las canciones en una lista de reproducción determinada. Los datos recuperados pueden guardarse en formatos JSON y Parquet sin procesar para su posterior procesamiento.

## Dependencias

Este proyecto requiere que se instalen las siguientes dependencias:

- `pandas`
- `spotipy`

## Configuración

Para usar la API de Spotify, se necesita un `client_id` y un `client_secret` que se pueden obtener al crear una aplicación en [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/). Estos valores se pueden proporcionar como variables de entorno o guardar en un archivo JSON. Si se opta por la opción de archivo JSON, se debe crear un archivo llamado `secret.json` dentro de un directorio llamado `credentials`. El formato del archivo es el siguiente:

```json
{
  "Spotify": {
    "CLIENT_ID": "your-client-id",
    "CLIENT_SECRET": "your-client-secret"
  }
}
```

## Uso

Para usar la clase `SpotifyAPI`, es necesario crear una instancia de la misma y luego llamar a sus métodos. Los siguientes métodos están disponibles:

- `get_playlist_data(playlist_id: str) -> None`: recupera todas las canciones en una lista de reproducción dada su identificación de Spotify.
- `get_playlist_info(playlist_id: str, user: str = None, fields: List[str] = None) -> Dict`: recupera información sobre una lista de reproducción dada su identificación de Spotify.
- `get_audio_features(song_id: Union[str, List[str]]) -> Dict`: recupera las características de audio de una canción dada su identificación de Spotify. Si se proporcionan múltiples identificaciones como una lista, se devolverá una lista de diccionarios con las características de cada canción.

Por ejemplo, para recuperar las características de audio de una sola canción:

```python
from classes.spotify import SpotifyAPI

spotify = SpotifyAPI()
song_id = "https://open.spotify.com/playlist/1jRjHPZ1H4fX3LU81FkwWR?si=e5f0577b120a4c92"
audio_features = spotify.get_audio_features(song_id)
```

Para recuperar todas las canciones en una lista de reproducción y guardar los datos sin procesar en formato JSON y los datos del modelo en formato PARQUET:

```python
from classes.spotify import SpotifyAPI

spotify = SpotifyAPI()
playlist_id = "https://open.spotify.com/playlist/1jRjHPZ1H4fX3LU81FkwWR?si=e5f0577b120a4c92"
spotify.get_playlist_data(playlist_id)
```

## Estructura de archivos

El proyecto tiene la siguiente estructura de archivos:

```
project/
│
├── api_data/
│   ├── <current-data YYYY-MM-DD>/
│        ├── <playlists-names>/
│            ├── parquet_data/
│            └── raw_data/
├── classes/
│   ├── __init__.py
│   ├── dev.py
│   ├── env.py
│   └── spotify.py
│
├── credentials/
│   └── secret.json
│
├── .gitignore
├── README.md
└── requirements.txt
```

- `classes/`: contiene la clase `SpotifyAPI`, así como otras clases y funciones de utilidad.
- `credentials/secret.json`: contiene las credenciales de la API de Spotify (ID de cliente y secreto de cliente).
- `.gitignore`: especifica los archivos y directorios que deben ser ignorados por Git.
- `README.md`: este archivo.
- `requirements.txt`: especifica las dependencias de Python requeridas por el proyecto.