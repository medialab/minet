from typing import List, Tuple, Optional, Iterator

import re
import json
from html import unescape
from urllib.parse import unquote
from ural import infer_redirection
from ebbe import getpath

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
INITIAL_DATA_RE = re.compile(
    rb"(?:const|let|var)\s+ytInitialData\s*=\s*({.+})\s*;</script>"
)


def gather_external_links(data) -> Iterator[Tuple[str, str]]:
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "channelExternalLinkViewModel":
                if not isinstance(v, dict):
                    return

                yield (
                    getpath(v, ("title", "content")).strip(),
                    infer_redirection(
                        getpath(
                            v,
                            (
                                "link",
                                "commandRuns",
                                0,
                                "onTap",
                                "innertubeCommand",
                                "urlEndpoint",
                                "url",
                            ),
                        )
                    ),
                )

                return

            yield from gather_external_links(v)

    elif isinstance(data, list):
        for v in data:
            yield from gather_external_links(v)

    else:
        return


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

    def get_channel_links(self, channel_url: str) -> Optional[List[Tuple[str, str]]]:
        # NOTE: for some weird reason, the /about page has more info in
        # the ytInitialData global variable even if visual content is
        # strictly identical.
        channel_url = channel_url.split("?", 1)[0].split("#")[0].rstrip("/") + "/about"

        response = self.request(channel_url, spoof_ua=True)

        match = INITIAL_DATA_RE.search(response.body)

        if match is None:
            return None

        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return None

        # with open("./dump.json", "w") as f:
        #     json.dump(data, f, ensure_ascii=False, indent=2)

        return list(gather_external_links(data))
