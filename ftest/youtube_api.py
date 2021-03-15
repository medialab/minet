from itertools import islice
from collections import Counter
from minet.cli.utils import get_rcfile
from minet.youtube import YouTubeAPIClient
from minet.youtube.scrapers import get_caption_tracks, select_caption_track

config = get_rcfile()

VIDEOS = [
    'psHGtkvSNwE',
    '9HOI3zSwhPg',
    'https://www.youtube.com/watch?v=1CpAygAF5nE',
    'nothing-to-see-here'
]

client = YouTubeAPIClient(config['youtube']['key'])

# for item, video in client.videos(VIDEOS):
#     print(item, video)

# for video in islice(client.search('"white rabbit tyto alba"'), 103):
#     print(video)

KROCK = 'DPzAvAlUJ24'
SCILABUS = 'https://www.youtube.com/watch?v=ARAQUgkdIvQ'

# count = 0
# ids = Counter()
# for comment in client.comments(SCILABUS, full_replies=True):
#     print(comment)
#     count += 1
#     ids[comment.comment_id] += 1

# print('Found %i comments.' % count)

# if ids.most_common(1)[0][1] > 1:
#     print('Found duplicated ids')

# xB-puVmmlg4
# eTiWhKcGpjw
# JaS8W3HMKY8
tracks = get_caption_tracks('https://www.youtube.com/watch?v=jsiY6s8-SJ8')
print([(t.lang, t.generated) for t in tracks])

print(select_caption_track(tracks, langs=['da', 'pt']))
