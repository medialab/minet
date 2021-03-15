# =============================================================================
# Minet Youtube Scrapers
# =============================================================================
#
# Collection of YouTube-related scrapers.
#
import re
import json
from urllib.parse import unquote
from collections import namedtuple

from minet.utils import create_pool, request
from minet.youtube.utils import ensure_video_id
from minet.youtube.exceptions import YouTubeInvalidVideoId

YOUTUBE_SCRAPER_POOL = create_pool()

CAPTION_TRACKS_RE = re.compile(r'({"captionTracks":.*isTranslatable":(true|false)}])')
TIMEDTEXT_RE = re.compile(rb'timedtext?[^"]+')

YouTubeCaptionTrack = namedtuple('YouTubeCaptionTrack', ['lang', 'url', 'generated'])


def get_caption_tracks(video_target):
    video_id = ensure_video_id(video_target)

    if video_id is None:
        raise YouTubeInvalidVideoId

    # First we try to retrieve it from video info
    url = 'https://www.youtube.com/get_video_info?video_id=%s' % video_id

    err, response = request(YOUTUBE_SCRAPER_POOL, url)

    if err:
        raise err

    data = unquote(response.data.decode('utf-8'))

    m = CAPTION_TRACKS_RE.search(data)

    if m is not None:
        data = json.loads(m.group(0) + '}')['captionTracks']

        return [
            YouTubeCaptionTrack(item['languageCode'], item['baseUrl'], item.get('kind') == 'asr')
            for item in data
        ]

    # Then we try to scrape it directly from the video page
    # url = 'https://www.youtube.com/watch?v=%s' % video_id

    # err, response = request(YOUTUBE_SCRAPER_POOL, url)

    # if err:
    #     raise err

    # timedtexts = TIMEDTEXT_RE.findall(response.data)

    return []
