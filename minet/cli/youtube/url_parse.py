from tqdm import tqdm
from ural.youtube import (
    parse_youtube_url,
    YoutubeVideo,
    YoutubeUser,
    YoutubeChannel
)

from minet.cli.utils import CSVEnricher

REPORT_HEADERS = ['youtube_type', 'youtube_id', 'youtube_name']

YOUTUBE_TYPES = {
    YoutubeVideo: 'video',
    YoutubeUser: 'user',
    YoutubeChannel: 'channel'
}


def url_parse(namespace, output_file):
    enricher = CSVEnricher(
        namespace.file,
        namespace.column,
        output_file,
        report_headers=REPORT_HEADERS,
        select=namespace.select.split(',') if namespace.select else None
    )

    loading_bar = tqdm(
        desc='Parsing',
        dynamic_ncols=True,
        unit=' lines',
    )

    for line in enricher:

        loading_bar.update()

        url_data = line[enricher.pos].strip()
        youtube_url = parse_youtube_url(url_data)
        if not youtube_url:
            enricher.write_empty(line)
            continue

        enricher.write(
            line,
            [YOUTUBE_TYPES.get(type(youtube_url)), youtube_url.id, getattr(youtube_url, 'name', None)]
        )
