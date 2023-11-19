""" Fetches currently playing song and artist from portuguese radio stations """

from typing import Optional
from dataclasses import dataclass
from xml.parsers.expat import ExpatError
import requests
import asyncio
import json
import aiohttp
from bs4 import BeautifulSoup
import xmltodict
from .urls import (
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


async def fetch_data_from_url(
    url: str, content_type: str
) -> Optional[aiohttp.ClientResponse]:
    """Fetches data from a given URL using aiohttp"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as response:
                return (
                    await getattr(response, content_type)()
                    if response.status == 200
                    else None
                )
        except aiohttp.ClientError:
            return None


async def _fetch_antenax(url: str) -> Optional[Song]:
    """Fetches currently playing song and artist from Antena X"""
    result = await fetch_data_from_url(url, "json")

    if result is not None:
        try:
            song_data = result[0]
            return Song.from_dict(song_data, "dtitulo", "dcoment1")
        except (json.JSONDecodeError, IndexError):
            pass

    return None


async def fetch_antena1() -> Optional[Song]:
    """Fetches currently playing song and artist from Antena 1"""
    return await _fetch_antenax(URL_ANTENA1)


async def fetch_antena3() -> Optional[Song]:
    """Fetches currently playing song and artist from Antena 3"""
    return await _fetch_antenax(URL_ANTENA3)


async def _fetch_bauer(url: str) -> Optional[Song]:
    """Fetches currently playing song and artist from Bauer Media"""
    result = await fetch_data_from_url(url, "text")
    if result is not None:
        try:
            parsed_data = xmltodict.parse(result)
            table = parsed_data.get("RadioInfo", {}).get("Table")
            if table:
                return Song.from_dict(
                    table, "DB_DALET_TITLE_NAME", "DB_DALET_ARTIST_NAME"
                )
        except (KeyError, ExpatError):
            pass
    return None


async def fetch_comercial() -> Optional[Song]:
    """Fetches currently playing song and artist from Comercial"""
    return await _fetch_bauer(URL_COMERCIAL)


async def fetch_m80() -> Optional[Song]:
    """Fetches currently playing song and artist from M80"""
    return await _fetch_bauer(URL_M80)


async def fetch_cidadefm() -> Optional[Song]:
    """Fetches currently playing song and artist from Cidade FM"""
    return await _fetch_bauer(URL_CIDADEFM)


async def fetch_smooth() -> Optional[Song]:
    """Fetches currently playing song and artist from Smooth FM"""
    return await _fetch_bauer(URL_SMOOTH)


async def fetch_futura() -> Optional[Song]:
    """Fetches currently playing song and artist from Futura"""
    result = await fetch_data_from_url(URL_FUTURA, "json")
    if result is not None:
        try:
            playing = result.get("data", {}).get("title")
            if playing:
                artist, title = map(str.strip, playing.split(" - ", maxsplit=1))
                return Song(title=title, artist=artist)

        except (KeyError, requests.exceptions.JSONDecodeError):
            pass
    return None


async def _fetch_php(url: str) -> Optional[Song]:
    """Fetches currently playing song and artist from .php links"""
    result = await fetch_data_from_url(url, "text")

    if result is not None:
        soup = BeautifulSoup(result, "html.parser")
        playing = soup.get_text().strip()
        try:
            artist, title = map(str.strip, playing.split(" - ", maxsplit=1))
            return Song(title=title, artist=artist)
        except ValueError:
            pass
    return None


async def fetch_radar() -> Optional[Song]:
    """Fetches currently playing song and artist from RadarFM"""
    return await _fetch_php(URL_RADAR)


async def fetch_oxigenio() -> Optional[Song]:
    """Fetches currently playing song and artist from RadarFM"""
    return await _fetch_php(URL_OXIGENIO)


async def _fetch_grm(url: str) -> Optional[Song]:
    """Fetches currently playing song and artist from Grupo Renascença Multimédia"""
    result = await fetch_data_from_url(url, "text")
    if result is not None:
        try:
            parsed_data = xmltodict.parse(result)
            table = parsed_data.get("music", {}).get("song")
            if table is not None:
                return Song.from_dict(table, "name", "artist")
        except (KeyError, ExpatError):
            pass
    return None


async def fetch_megahits() -> Optional[Song]:
    """Fetches currently playing song and artist from RFM"""
    return await _fetch_grm(URL_MEGAHITS)


async def fetch_renascenca() -> Optional[Song]:
    """Fetches currently playing song and artist from RFM"""
    return await _fetch_grm(URL_RENASCENCA)


async def fetch_rfm() -> Optional[Song]:
    """Fetches currently playing song and artist from RFM"""
    return await _fetch_grm(URL_RFM)


async def fetch_sbsr() -> Optional[Song]:
    """Fetches currently playing song and artist from SBSR"""
    result = await fetch_data_from_url(URL_SBSR, "text")
    if result is not None:
        try:
            parsed_data = xmltodict.parse(result)
            current = parsed_data.get("BroadcastMonitor", {}).get("Current")
            if current is not None:
                return Song.from_dict(current, "titleName", "artistName")
        except (KeyError, ExpatError):
            pass

    return None


async def main():
    tasks = [
        asyncio.create_task(fetch_antena1()),
        asyncio.create_task(fetch_antena3()),
        asyncio.create_task(fetch_comercial()),
        asyncio.create_task(fetch_m80()),
        asyncio.create_task(fetch_cidadefm()),
        asyncio.create_task(fetch_smooth()),
        asyncio.create_task(fetch_futura()),
        asyncio.create_task(fetch_radar()),
        asyncio.create_task(fetch_oxigenio()),
        asyncio.create_task(fetch_sbsr()),
        asyncio.create_task(fetch_megahits()),
        asyncio.create_task(fetch_renascenca()),
        asyncio.create_task(fetch_rfm()),
    ]

    results = await asyncio.gather(*tasks)
    for radio, result in zip(
        [
            "Antena1",
            "Antena3",
            "Comercial",
            "M80",
            "CidadeFM",
            "Smooth",
            "Futura",
            "Radar",
            "Oxigenio",
            "SBSR",
            "MegaHits",
            "Renascenca",
            "RFM",
        ],
        results,
    ):
        print(f"{radio}: {result}")


if __name__ == "__main__":
    asyncio.run(main())
