import re
from typing import Dict

import requests
from bs4 import BeautifulSoup

from classes import dev


def get_billboard_hot_100(date: bool = True) -> Dict:
    """
    Devuelve un diccionario con las 100 canciones más populares en Billboard en una fecha específica o en la fecha actual.

    Args:
        date (bool, optional): Fecha en formato YYYY-MM-DD. Si es True, se usará la fecha actual. Default: True.

    Returns:
        dict: Diccionario con las claves como nombres de las canciones y los valores como nombres de los artistas.

    """

    # Si date es True, se obtiene la fecha actual
    if date:
        date = dev.validar_fecha()
        url = f"https://www.billboard.com/charts/hot-100/{date}"

    # Si date es False, se usa la url de la fecha actual
    else:
        url = f"https://www.billboard.com/charts/hot-100/"

    # Se hace una solicitud GET a la url especificada
    response = requests.get(url)

    # Se crea un objeto BeautifulSoup para procesar el HTML de la página
    soup = BeautifulSoup(response.text, "html.parser")

    # Se obtiene el nombre de la canción en el primer lugar de la lista
    top_one_song = (
        soup.find(
            "h3",
            class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 u-max-width-230@tablet-only u-letter-spacing-0028@tablet",
        )
        .get_text()
        .strip()
    )

    # Se obtienen todos los nombres de las canciones y artistas en la lista
    song_tags = soup.find_all(
        "h3",
        class_=re.compile(
            "c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only"
        ),
    )
    artist_tags = soup.find_all(
        "span",
        class_=re.compile(
            "c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only"
        ),
    )

    # Se guardan los nombres de las canciones y artistas en listas separadas
    songs = [tag.get_text().strip() for tag in song_tags]
    artist = [tag.get_text().strip() for tag in artist_tags]

    # Se agrega el nombre de la canción en el primer lugar de la lista
    songs.insert(0, top_one_song)

    # Se crea un diccionario con las claves como nombres de las canciones y los valores como nombres de los artistas
    return dict(zip(songs, artist))
