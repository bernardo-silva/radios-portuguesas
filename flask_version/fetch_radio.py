""" Fetches currently playing song and artist from portuguese radio stations """

from typing import Optional
from dataclasses import dataclass
from xml.parsers.expat import ExpatError
import requests
from bs4 import BeautifulSoup
import xmltodict
from urls import (
    URL_ANTENA1,
    URL_ANTENA3,
    URL_COMERCIAL,
    URL_M80,
    URL_CIDADEFM,
    URL_FUTURA,
    URL_OXIGENIO,
    URL_RADAR,
    URL_SBSR,
    URL_MEGAHITS,
    URL_RENASCENCA,
    URL_RFM,
    URL_SMOOTH,
)


@dataclass
class Song:
    """Song dataclass"""

    title: str
    artist: str

    @classmethod
    def from_dict(
        cls, data: dict["str", "str"], title_key: str, artist_key: str
    ) -> Optional["Song"]:
        """Parse song and artist information from a dictionary."""

        try:
            title = data[title_key]
            artist = data[artist_key]
            return cls(title=title, artist=artist)
        except KeyError:
            return None


def fetch_data_from_url(url: str) -> Optional[requests.Response]:
    """Fetches data from a given url"""
    try:
        result = requests.get(url, timeout=5)
        result.encoding = result.apparent_encoding
        return result
    except requests.exceptions.RequestException:
        return None


def _fetch_antenax(url: str) -> Optional[Song]:
    """Fetches currently playing song and artist from Antena X"""
    result = fetch_data_from_url(url)
    if result is not None:
        try:
            return Song.from_dict(result.json()[0], "dtitulo", "dcoment1")
        except requests.exceptions.JSONDecodeError:
            pass
    return None


def fetch_antena1() -> Optional[Song]:
    """Fetches currently playing song and artist from Antena 1"""
    return _fetch_antenax(URL_ANTENA1)


def fetch_antena3() -> Optional[Song]:
    """Fetches currently playing song and artist from Antena 3"""
    return _fetch_antenax(URL_ANTENA3)


def _fetch_bauer(url: str) -> Optional[Song]:
    """Fetches currently playing song and artist from Bauer Media"""
    result = fetch_data_from_url(url)
    if result is not None:
        try:
            parsed_data = xmltodict.parse(result.text)
            table = parsed_data.get("RadioInfo", {}).get("Table")
            if table:
                return Song.from_dict(
                    table, "DB_DALET_TITLE_NAME", "DB_DALET_ARTIST_NAME"
                )
        except (KeyError, ExpatError):
            pass
    return None


def fetch_comercial() -> Optional[Song]:
    """Fetches currently playing song and artist from Comercial"""
    return _fetch_bauer(URL_COMERCIAL)


def fetch_m80() -> Optional[Song]:
    """Fetches currently playing song and artist from M80"""
    return _fetch_bauer(URL_M80)


def fetch_cidadefm() -> Optional[Song]:
    """Fetches currently playing song and artist from Cidade FM"""
    return _fetch_bauer(URL_CIDADEFM)


def fetch_smooth() -> Optional[Song]:
    """Fetches currently playing song and artist from Smooth FM"""
    return _fetch_bauer(URL_SMOOTH)


def fetch_futura() -> Optional[Song]:
    """Fetches currently playing song and artist from Futura"""
    result = fetch_data_from_url(URL_FUTURA)
    if result is not None:
        try:
            playing = result.json().get("data", {}).get("title")
            if playing:
                artist, title = map(str.strip, playing.split(" - ", maxsplit=1))
                return Song(title=title, artist=artist)

        except (KeyError, requests.exceptions.JSONDecodeError):
            pass
    return None


def _fetch_php(url: str) -> Optional[Song]:
    """Fetches currently playing song and artist from .php links"""
    result = fetch_data_from_url(url)

    if result is not None:
        soup = BeautifulSoup(result.text, "html.parser")
        playing = soup.get_text().strip()
        try:
            artist, title = map(str.strip, playing.split(" - ", maxsplit=1))
            return Song(title=title, artist=artist)
        except ValueError:
            pass
    return None


def fetch_radar() -> Optional[Song]:
    """Fetches currently playing song and artist from RadarFM"""
    return _fetch_php(URL_RADAR)


def fetch_oxigenio() -> Optional[Song]:
    """Fetches currently playing song and artist from RadarFM"""
    return _fetch_php(URL_OXIGENIO)


def _fetch_grm(url: str) -> Optional[Song]:
    """Fetches currently playing song and artist from Grupo Renascença Multimédia"""
    result = fetch_data_from_url(url)
    if result is not None:
        try:
            parsed_data = xmltodict.parse(result.text)
            table = parsed_data.get("music", {}).get("song")
            if table:
                return Song.from_dict(table, "name", "artist")
        except (KeyError, ExpatError):
            pass
    return None


def fetch_megahits() -> Optional[Song]:
    """Fetches currently playing song and artist from RFM"""
    return _fetch_grm(URL_MEGAHITS)


def fetch_renascenca() -> Optional[Song]:
    """Fetches currently playing song and artist from RFM"""
    return _fetch_grm(URL_RENASCENCA)


def fetch_rfm() -> Optional[Song]:
    """Fetches currently playing song and artist from RFM"""
    return _fetch_grm(URL_RFM)


def fetch_sbsr() -> Optional[Song]:
    """Fetches currently playing song and artist from SBSR"""
    result = fetch_data_from_url(URL_SBSR)
    if result is not None:
        try:
            parsed_data = xmltodict.parse(result.text)
            current = parsed_data.get("BroadcastMonitor", {}).get("Current")
            if current is not None:
                return Song.from_dict(current, "titleName", "artistName")
        except (KeyError, ExpatError):
            pass

    return None


if __name__ == "__main__":
    print("Antena1: ", fetch_antena1())
    print("Antena3: ", fetch_antena3())

    print("Comercial: ", fetch_comercial())
    print("M80: ", fetch_m80())
    print("CidadeFM: ", fetch_cidadefm())
    print("Smooth: ", fetch_smooth())

    print("Futura: ", fetch_futura())
    print("Radar: ", fetch_radar())
    print("Oxigenio: ", fetch_oxigenio())
    print("SBSR: ", fetch_sbsr())

    print("MegaHits: ", fetch_megahits())
    print("Renascenca: ", fetch_renascenca())
    print("RFM: ", fetch_rfm())
