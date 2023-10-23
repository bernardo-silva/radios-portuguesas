from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint

@dataclass
class SpotifySong:
    title: str
    artist: str
    image_url: str = ""
    spotify_url: str = ""

    @classmethod
    def from_search(cls, title: str, artist: str) -> Optional["SpotifySong"]:
        load_dotenv()
        auth_manager = SpotifyOAuth()
        sp = spotipy.Spotify(auth_manager=auth_manager)

        results = sp.search(q=f"track:{title} artist:{artist}", type="track")
        tracks = results.get("tracks", {}).get("items")

        if tracks is not None and tracks:
            track = tracks[0]

            title = track["name"]
            artists = " | ".join(artist["name"] for artist in track["artists"])
            image = track["album"]["images"][0]["url"]
            url = track["external_urls"]["spotify"]

            return cls(title, artists, image, url)
        return None

if __name__ == "__main__":
    from fetch_radio import *
    song = fetch_antena1()
    print(song)
    print(SpotifySong.from_search(song.title, song.artist))

