from typing import List, Dict, Any

from dataclasses import dataclass
from casanova import TabularRecord


@dataclass
class SpotifyShow(TabularRecord):
    id: str
    type: str
    name: str
    publisher: str
    description: str
    html_description: str
    explicit: bool
    languages: List[str]
    total_episodes: int
    available_markets: List[str]
    url: str

    @classmethod
    def from_payload(cls, item: Dict[str, Any]) -> "SpotifyShow":
        return cls(
            id=item["id"],
            type=item["type"],
            name=item["name"],
            publisher=item["publisher"],
            description=item["description"],
            html_description=item["html_description"],
            explicit=item["explicit"],
            languages=item["languages"],
            total_episodes=item["total_episodes"],
            available_markets=item["available_markets"],
            url=item["external_urls"]["spotify"],
        )


@dataclass
class SpotifyShowEpisode(TabularRecord):
    id: str
    type: str
    name: str
    release_date: str
    release_date_precision: str
    language: str
    languages: List[str]
    duration: int
    explicit: bool
    description: str
    html_description: str
    url: str

    @classmethod
    def from_payload(cls, item: Dict[str, Any]) -> "SpotifyShowEpisode":
        return cls(
            id=item["id"],
            type=item["type"],
            name=item["name"],
            release_date=item["release_date"],
            release_date_precision=item["release_date_precision"],
            language=item["language"],
            languages=item["languages"],
            duration=item["duration_ms"],
            explicit=item["explicit"],
            description=item["description"],
            html_description=item["html_description"],
            url=item["external_urls"]["spotify"],
        )
