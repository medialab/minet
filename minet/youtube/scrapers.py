# =============================================================================
# Minet Youtube Scrapers
# =============================================================================
#
# Collection of YouTube-related scrapers.
#
from typing import Optional

import re
import json
from html import unescape
from urllib.parse import unquote
from collections import namedtuple

from minet.scrape import WonderfulSoup
from minet.web import request, create_pool_manager
from minet.youtube.utils import ensure_video_id
from minet.youtube.exceptions import YouTubeInvalidVideoTargetError

CAPTION_TRACKS_RE = re.compile(r'"captionTracks":(\[.*?\])')

YOUTUBE_SCRAPER_POOL_MANAGER = create_pool_manager()

YouTubeCaptionTrack = namedtuple("YouTubeCaptionTrack", ["lang", "url", "generated"])


# Hats off to: https://github.com/algolia/youtube-captions-scraper
def get_caption_tracks(video_id):
    # First we try to retrieve it from video info
    url = "https://www.youtube.com/watch?v=%s" % video_id

    response = request(
        url, known_encoding="utf-8", pool_manager=YOUTUBE_SCRAPER_POOL_MANAGER
    )

    data = unquote(response.text())

    m = CAPTION_TRACKS_RE.search(data)

    if m is not None:
        data = json.loads("{" + m.group(0) + "}")["captionTracks"]

        return [
            YouTubeCaptionTrack(
                item["languageCode"], item["baseUrl"], item.get("kind") == "asr"
            )
            for item in data
        ]

    return []


def select_caption_track(tracks, langs=None, strict=True):
    def key(t):
        try:
            return (langs.index(t.lang), int(t.generated), t.lang)
        except ValueError:
            return (len(langs), int(t.generated), t.lang)

    best = min(tracks, key=key)

    if strict and best.lang not in langs:
        return None

    return best


def get_video_captions(video_target, langs):
    if not isinstance(langs, list):
        raise TypeError

    video_id = ensure_video_id(video_target)

    if video_id is None:
        raise YouTubeInvalidVideoTargetError

    tracks = get_caption_tracks(video_id)

    if not tracks:
        return

    best_track = select_caption_track(tracks, langs=langs)

    if best_track is None:
        return

    response = request(
        best_track.url,
        pool_manager=YOUTUBE_SCRAPER_POOL_MANAGER,
        known_encoding="utf-8",
    )

    soup = WonderfulSoup(response.text(), "xml")

    captions = []

    for item in soup.select("text"):
        captions.append(
            (item.get("start"), item.get("dur"), unescape(item.get_text().strip()))
        )

    return best_track, captions


def scrape_channel_id(channel_url: str) -> Optional[str]:
    response = request(
        channel_url,
        pool_manager=YOUTUBE_SCRAPER_POOL_MANAGER,
        known_encoding="utf-8",
        spoof_ua=True,
    )

    soup = WonderfulSoup(response.text(), "lxml")
    tag = soup.find("meta", {"itemprop": "identifier"})

    if tag:
        return tag.get("content")
