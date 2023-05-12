# Spotify API

This project consists of a Python module that provides a simplified interface to the Spotify Web API, which allows the retrieval of various data about songs, artists, albums, and playlists. The `SpotifyAPI` class provides methods to retrieve audio features and playlist information, as well as all the tracks in a given playlist. The retrieved data can be saved in raw JSON and Parquet formats for further processing.

## Dependencies

This project requires the following dependencies to be installed:

- `pandas`
- `spotipy`

## Usage

To use the `SpotifyAPI` class, you need to create an instance of it and then call its methods. The following methods are available:

- `get_audio_features(song_uri: Union[str, List[str]]) -> Dict`: retrieves the audio features of a song given its Spotify URI. If multiple URIs are provided as a list, a list of dictionaries with the features of each song will be returned.
- `get_playlist_info(playlist_id: str, user: str = None, fields: List[str] = None) -> Dict`: retrieves information about a playlist given its Spotify URI.
- `get_playlist_data(playlist_id: str) -> Tuple[List[Dict], str]`: retrieves all the tracks in a playlist given its Spotify URI. The method returns a tuple containing a list of dictionaries with the data of each track and the name of the playlist.

For example, to retrieve the audio features of a single song:

```python
from classes.spotify import SpotifyAPI

spotify = SpotifyAPI()
song_uri = "spotify:track:3Zwu2KlBkJ2iYFQd7Xvz9y"
audio_features = spotify.get_audio_features(song_uri)
```

To retrieve all the tracks in a playlist and save the raw data in JSON format:

```python
from classes.spotify import SpotifyAPI

spotify = SpotifyAPI()
playlist_id = "spotify:playlist:37i9dQZEVXbMDoHDwVN2tF"
tracks, playlist_name = spotify.get_playlist_data(playlist_id)
```

## File Structure

The project has the following file structure:

```
project/
│
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

- `classes/`: contains the `SpotifyAPI` class, as well as other utility classes and functions.
- `credentials/secret.json`: contains the Spotify API credentials (client ID and client secret).
- `.gitignore`: specifies files and directories to be ignored by Git.
- `README.md`: this file.
- `requirements.txt`: specifies the Python dependencies required by the project.