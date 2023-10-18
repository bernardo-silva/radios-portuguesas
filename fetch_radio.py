""" Fetches currently playing song and artist from portuguese radio stations """

from typing import Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import xmltodict
from urls import (
    URL_RADAR,
    URL_COMERCIAL,
)

@dataclass
class Song:
    """ Song dataclass """
    title: str
    artist: str

def fetch_radar() -> Optional[Song]:
    """ Fetches currently playing song and artist from RadarFM """
    playing = BeautifulSoup(requests.get(URL_RADAR).text,
                            "html.parser").get_text().strip()

    try:
        artist, title = map(str.strip, playing.split(" - ", maxsplit=1))
    except ValueError:
        return None

    return Song(title=title, artist=artist)

def fetch_comercial() -> Optional[Song]:
    """ Fetches currently playing song and artist from Comercial """
    result = xmltodict.parse(requests.get(URL_COMERCIAL).text)
    try:
        playing = result["RadioInfo"]["Table"]
        title = playing["DB_DALET_TITLE_NAME"]
        artist = playing["DB_DALET_ARTIST_NAME"]

    except AttributeError:
        return None

    return Song(title=title, artist=artist)


if __name__ == "__main__":
    print("Radar: ", fetch_radar())
    print("Comercial: ", fetch_comercial())
