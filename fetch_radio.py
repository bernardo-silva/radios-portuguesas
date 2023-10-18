""" Fetches currently playing song and artist from portuguese radio stations """

from typing import Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import xmltodict
from urls import (
    URL_ANTENA1,
    URL_ANTENA3,
    URL_COMERCIAL,
    URL_M80,
    URL_RADAR,
    URL_RFM,
)


@dataclass
class Song:
    """Song dataclass"""

    title: str
    artist: str


def _fetch_antenax(url: str) -> Optional[Song]:
    """Fetches currently playing song and artist from Antena X"""
    result = requests.get(url, timeout=5).json()
    try:
        playing = result[0]
        title = playing["dtitulo"]
        artist = playing["dcoment1"]

    except AttributeError:
        return None

    return Song(title=title, artist=artist)


def fetch_antena1() -> Optional[Song]:
    """Fetches currently playing song and artist from Antena 1"""
    return _fetch_antenax(URL_ANTENA1)


def fetch_antena3() -> Optional[Song]:
    """Fetches currently playing song and artist from Antena 3"""
    return _fetch_antenax(URL_ANTENA3)


def fetch_comercial() -> Optional[Song]:
    """Fetches currently playing song and artist from Comercial"""
    result = xmltodict.parse(requests.get(URL_COMERCIAL, timeout=5).text)
    try:
        playing = result["RadioInfo"]["Table"]
        title = playing["DB_DALET_TITLE_NAME"]
        artist = playing["DB_DALET_ARTIST_NAME"]

    except AttributeError:
        return None

    return Song(title=title, artist=artist)


def fetch_m80() -> Optional[Song]:
    """Fetches currently playing song and artist from M80"""
    result = xmltodict.parse(requests.get(URL_M80, timeout=5).text)
    try:
        playing = result["RadioInfo"]["Table"]
        title = playing["DB_DALET_TITLE_NAME"]
        artist = playing["DB_DALET_ARTIST_NAME"]

    except AttributeError:
        return None

    return Song(title=title, artist=artist)


def fetch_radar() -> Optional[Song]:
    """Fetches currently playing song and artist from RadarFM"""
    playing = (
        BeautifulSoup(requests.get(URL_RADAR, timeout=5).text, "html.parser")
        .get_text()
        .strip()
    )

    try:
        artist, title = map(str.strip, playing.split(" - ", maxsplit=1))
    except ValueError:
        return None

    return Song(title=title, artist=artist)


def fetch_rfm() -> Optional[Song]:
    """Fetches currently playing song and artist from RFM"""
    result = xmltodict.parse(requests.get(URL_RFM, timeout=5).text)

    try:
        playing = result["music"]["song"]
        title = playing["name"]
        artist = playing["artist"]
    except AttributeError:
        return None

    return Song(title=title, artist=artist)


if __name__ == "__main__":
    print("Antena1: ", fetch_antena1())
    print("Antena3: ", fetch_antena3())
    print("Comercial: ", fetch_comercial())
    print("M80: ", fetch_m80())
    print("Radar: ", fetch_radar())
    print("RFM: ", fetch_rfm())
