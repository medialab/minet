# =============================================================================
# Minet Youtube Url Parse CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and parsing the Youtube urls
# contained in a given column.
#
import casanova
from tqdm import tqdm
from ural.youtube import (
    parse_youtube_url,
    YoutubeVideo,
    YoutubeUser,
    YoutubeChannel
)

REPORT_HEADERS = ['youtube_type', 'youtube_id', 'youtube_name']

YOUTUBE_TYPES = {
    YoutubeVideo: 'video',
    YoutubeUser: 'user',
    YoutubeChannel: 'channel'
}


def url_parse_action(namespace, output_file):
    enricher = casanova.enricher(
        namespace.file,
        output_file,
        add=REPORT_HEADERS,
        keep=namespace.select
    )

    loading_bar = tqdm(
        desc='Parsing',
        dynamic_ncols=True,
        unit=' lines',
    )

    for row, url in enricher.cells(namespace.column, with_rows=True):

        loading_bar.update()

        url = url.strip()
        youtube_url = parse_youtube_url(url)

        if not youtube_url:
            enricher.writerow(row)
            continue

        enricher.writerow(
            row,
            [YOUTUBE_TYPES.get(type(youtube_url)), youtube_url.id, getattr(youtube_url, 'name', None)]
        )
