from casanova import TabularRecord
from dataclasses import dataclass


@dataclass
class YouTubeCaptionTrack(TabularRecord):
    lang: str
    url: str
    generated: bool


@dataclass
class YouTubeCaptionLine(TabularRecord):
    start: float
    duration: float
    text: str
