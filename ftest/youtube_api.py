from itertools import islice
from minet.cli.utils import get_rcfile
from minet.youtube import YouTubeAPIClient

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

count = 0
for comment in client.comments('DPzAvAlUJ24'):
    print(comment)
    count += 1

print('Found %i comments.' % count)
