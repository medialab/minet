# =============================================================================
# Minet Youtube Scrapers
# =============================================================================
#
# Collection of YouTube-related scrapers.
#
import re
import json
from bs4 import BeautifulSoup
from html import unescape
from urllib.parse import unquote
from collections import namedtuple

from minet.web import request, create_pool
from minet.youtube.utils import ensure_video_id
from minet.youtube.exceptions import YouTubeInvalidVideoTargetError

CAPTION_TRACKS_RE = re.compile(r'({"captionTracks":.*isTranslatable":(true|false)}])')
TIMEDTEXT_RE = re.compile(rb'timedtext?[^"]+')

YOUTUBE_SCRAPER_POOL = create_pool()

YouTubeCaptionTrack = namedtuple("YouTubeCaptionTrack", ["lang", "url", "generated"])


def get_caption_tracks(video_id):

    # First we try to retrieve it from video info
    url = "https://www.youtube.com/get_video_info?video_id=%s" % video_id

    err, response = request(url)

    if err:
        raise err

    data = unquote(response.data.decode("utf-8"))

    m = CAPTION_TRACKS_RE.search(data)

    if m is not None:
        data = json.loads(m.group(0) + "}")["captionTracks"]

        return [
            YouTubeCaptionTrack(
                item["languageCode"], item["baseUrl"], item.get("kind") == "asr"
            )
            for item in data
        ]

    # Then we try to scrape it directly from the video page
    # url = 'https://www.youtube.com/watch?v=%s' % video_id

    # err, response = request(url)

    # if err:
    #     raise err

    # timedtexts = TIMEDTEXT_RE.findall(response.data)

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

    err, response = request(best_track.url, pool=YOUTUBE_SCRAPER_POOL)

    if err:
        raise err

    soup = BeautifulSoup(response.data.decode("utf-8"), "lxml")

    captions = []

    for item in soup.select("text"):
        captions.append(
            (item.get("start"), item.get("dur"), unescape(item.get_text().strip()))
        )

    return best_track, captions


def scrape_channel_id(channel_url):
    err, response = request(channel_url, pool=YOUTUBE_SCRAPER_POOL)

    if err:
        raise err

    soup = BeautifulSoup(response.data.decode("utf-8"), "lxml")
    tag = soup.find("meta", {"itemprop": "channelId"})
    if tag:
        return tag.get("content")
