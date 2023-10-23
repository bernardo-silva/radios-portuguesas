from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Callable
from spotify import SpotifySong
from fetch_radio import (
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


@dataclass
class Radio:
    """Represents a radio station"""

    name: str
    url: str
    img: str
    fetch_function: Callable
    current_song: Optional[SpotifySong] = None
    last_update: Optional[datetime] = None


def available_radios() -> dict[str, Radio]:
    return {
        "antena1": Radio("Antena1", "", "", fetch_antena1),
        "antena3": Radio("Antena3", "", "", fetch_antena3),
        "comercial": Radio("Comercial", "", "", fetch_comercial),
        "m80": Radio("M80", "", "", fetch_m80),
        "cidadefm": Radio("CidadeFM", "", "", fetch_cidadefm),
        "smooth": Radio("Smooth", "", "", fetch_smooth),
        "futura": Radio("Futura", "", "", fetch_futura),
        "radar": Radio("Radar", "", "", fetch_radar),
        "oxigenio": Radio("Oxigénio", "", "", fetch_oxigenio),
        "sbsr": Radio("SBSR", "", "", fetch_sbsr),
        "megahits": Radio("Megahits", "", "", fetch_megahits),
        "renascenca": Radio("Renascença", "", "", fetch_renascenca),
        "rfm": Radio("RFM", "", "", fetch_rfm),
    }
