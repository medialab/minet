from typing import List, Tuple, Optional

import re
import json
from html import unescape
from urllib.parse import unquote

from minet.scrape import WonderfulSoup
from minet.web import (
    create_pool_manager,
    create_request_retryer,
    request,
    retrying_method,
    Response,
)

from minet.youtube.types import YouTubeCaptionTrack, YouTubeCaptionLine
from minet.youtube.utils import ensure_video_id
from minet.youtube.exceptions import YouTubeInvalidVideoTargetError


CAPTION_TRACKS_RE = re.compile(r'"captionTracks":(\[.*?\])')


def select_caption_track(
    tracks: List[YouTubeCaptionTrack], langs: List[str], strict: bool = True
) -> Optional[YouTubeCaptionTrack]:
    def key(t):
        try:
            return (langs.index(t.lang), int(t.generated), t.lang)
        except ValueError:
            return (len(langs), int(t.generated), t.lang)

    best = min(tracks, key=key)

    if strict and best.lang not in langs:
        return None

    return best


class YouTubeScraper:
    def __init__(self):
        self.pool_manager = create_pool_manager()
        self.retryer = create_request_retryer()

    @retrying_method()
    def request(self, url, spoof_ua: bool = False) -> Response:
        return request(
            url,
            pool_manager=self.pool_manager,
            spoof_ua=spoof_ua,
        )

    # Hats off to: https://github.com/algolia/youtube-captions-scraper
    def get_caption_tracks(self, video_id: str) -> List[YouTubeCaptionTrack]:
        # First we try to retrieve it from video info
        url = "https://www.youtube.com/watch?v=%s" % video_id

        response = self.request(url)

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

    def get_video_captions(
        self, video_target: str, langs: List[str] = ["en"]
    ) -> Optional[Tuple[YouTubeCaptionTrack, List[YouTubeCaptionLine]]]:
        video_id = ensure_video_id(video_target)

        if video_id is None:
            raise YouTubeInvalidVideoTargetError

        tracks = self.get_caption_tracks(video_id)

        if not tracks:
            return

        best_track = select_caption_track(tracks, langs=langs)

        if best_track is None:
            return

        response = self.request(best_track.url)

        soup = WonderfulSoup(response.text(), "xml")

        captions = []

        for item in soup.select("text"):
            # NOTE: sometimes duration is absent. I don't really
            # know what is the best solution there (merging with
            # previous item?). So for now, we default duration to 0.
            captions.append(
                YouTubeCaptionLine(
                    float(item["start"]),
                    float(item.get("dur", "0")),
                    unescape(item.get_text().strip()),
                )
            )

        return best_track, captions

    def get_channel_id(self, channel_url: str) -> Optional[str]:
        response = self.request(
            channel_url,
            spoof_ua=True,
        )

        soup = WonderfulSoup(response.text(), "lxml")
        tag = soup.select_one("meta[itemprop=identifier]")

        if tag:
            return tag.get("content")

        return None
