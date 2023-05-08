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
    href: str

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
            href=item["href"],
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
    href: str
    show_id: str
    show_name: str
    show_publisher: str
    show_description: str
    show_html_description: str
    show_explicit: bool
    show_languages: List[str]
    show_total_episodes: int
    show_available_markets: List[str]
    show_href: str

    @classmethod
    def from_payload(cls, item: Dict[str, Any]) -> "SpotifyShowEpisode":
        if item.get("show"):
            item.update(
                {
                    "show_id": item["show"]["id"],
                    "show_name": item["show"]["name"],
                    "show_publisher": item["show"]["publisher"],
                    "show_description": item["show"]["description"],
                    "show_html_description": item["show"]["html_description"],
                    "show_explicit": item["show"]["explicit"],
                    "show_languages": item["show"]["languages"],
                    "show_total_episodes": item["show"]["total_episodes"],
                    "show_available_markets": item["show"]["available_markets"],
                    "show_href": item["show"]["href"],
                }
            )
        else:
            item.update(
                {
                    "show_id": None,
                    "show_name": None,
                    "show_publisher": None,
                    "show_description": None,
                    "show_html_description": None,
                    "show_explicit": None,
                    "show_languages": None,
                    "show_total_episodes": None,
                    "show_available_markets": None,
                    "show_href": None,
                }
            )
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
            href=item["external_urls"]["spotify"],
            show_id=item["show_id"],
            show_name=item["show_name"],
            show_publisher=item["show_publisher"],
            show_description=item["show_description"],
            show_html_description=item["show_html_description"],
            show_explicit=item["show_explicit"],
            show_languages=item["show_languages"],
            show_total_episodes=item["show_total_episodes"],
            show_available_markets=item["show_available_markets"],
            show_href=item["show_href"],
        )
