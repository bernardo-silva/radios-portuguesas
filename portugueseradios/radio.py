from dataclasses import dataclass
from datetime import datetime
import asyncio
from logging import getLogger
from typing import Optional, Callable
from .spotify import SpotifySong
from .fetch_radio import (
    Song,
    fetch_antena1,
    fetch_antena3,
    fetch_comercial,
    fetch_m80,
    fetch_cidadefm,
    fetch_smooth,
    fetch_futura,
    fetch_radar,
    fetch_oxigenio,
    fetch_sbsr,
    fetch_megahits,
    fetch_renascenca,
    fetch_rfm,
)

logger = getLogger(__name__)


@dataclass
class Radio:
    """Represents a radio station"""

    name: str
    url: str
    image: str
    fetch_function: Callable
    last_song: Optional[Song] = None
    current_song: Optional[SpotifySong] = None
    last_update: Optional[datetime] = None

    async def fetch(self) -> bool:
        song = await self.fetch_function()
        if song is not None and song != self.last_song:
            self.last_song = song
            self.last_update = datetime.now()
            self.current_song = SpotifySong.from_search(song.title, song.artist)
            return True
        return False

    async def poll(self, interval: int, queue: asyncio.Queue):
        while True:
            updated = await self.fetch()
            if updated:
                await queue.put(self)
            # print(f"Updated {self.name}")
            await asyncio.sleep(interval)


def available_radios() -> list[Radio]:
    return [
        Radio("Antena1", "", "images/antena1.webp", fetch_antena1),
        Radio(
            "Antena3",
            "https://www.rtp.pt/play/popup/antena3",
            "images/antena3.webp",
            fetch_antena3,
        ),
        Radio("CidadeFM", "", "", fetch_cidadefm),
        Radio("Comercial", "", "images/comercial.svg", fetch_comercial),
        # Radio("Futura", "", "", fetch_futura),
        Radio("M80", "", "images/m80.svg", fetch_m80),
        Radio(
            "Megahits",
            "https://megahits.sapo.pt/",
            "images/megahits.svg",
            fetch_megahits,
        ),
        Radio("Oxigénio", "https://oxigenio.fm", "images/oxigenio.png", fetch_oxigenio),
        Radio("RFM", "", "images/rfm.png", fetch_rfm),
        Radio("Radar", "https://radarlisboa.fm", "images/radar.png", fetch_radar),
        Radio("Renascença", "", "", fetch_renascenca),
        Radio("SBSR", "https://sbsr.fm", "images/sbsr.png", fetch_sbsr),
        Radio("Smooth", "https://smoothfm.pt/", "images/smoothfm.svg", fetch_smooth),
    ]

    # return {
    #     "antena1": Radio("Antena1", "", "", fetch_antena1),
    #     "antena3": Radio("Antena3", "", "", fetch_antena3),
    #     "comercial": Radio("Comercial", "", "", fetch_comercial),
    #     "m80": Radio("M80", "", "", fetch_m80),
    #     "cidadefm": Radio("CidadeFM", "", "", fetch_cidadefm),
    #     "smooth": Radio("Smooth", "", "", fetch_smooth),
    #     "futura": Radio("Futura", "", "", fetch_futura),
    #     "radar": Radio("Radar", "", "", fetch_radar),
    #     "oxigenio": Radio("Oxigénio", "", "", fetch_oxigenio),
    #     "sbsr": Radio("SBSR", "", "", fetch_sbsr),
    #     "megahits": Radio("Megahits", "", "", fetch_megahits),
    #     "renascenca": Radio("Renascença", "", "", fetch_renascenca),
    #     "rfm": Radio("RFM", "", "", fetch_rfm),
    # }
