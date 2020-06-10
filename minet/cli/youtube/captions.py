# =============================================================================
# Minet Youtube Captions CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving caption about
# the given Youtube videos.
#
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
from minet.cli.utils import CSVEnricher, die
from minet.utils import create_pool, request_json, request
from ural.youtube import (
    extract_video_id_from_youtube_url,
    is_youtube_video_id,
    is_youtube_url
)

REPORT_HEADERS = [
    'caption_text'
]

CAPTIONS_URL_TEMPLATE = 'https://www.youtube.com/api/timedtext?lang=%(lg)s&v=%(id)s'

def captions_action(namespace, output_file):

    enricher = CSVEnricher(
        namespace.file,
        namespace.column,
        output_file,
        report_headers=REPORT_HEADERS,
        select=namespace.select.split(',') if namespace.select else None
    )

    loading_bar = tqdm(
        desc='Retrieving',
        dynamic_ncols=True,
        unit=' videos',
    )

    http = create_pool()

    for line in enricher:

        video_id = line[enricher.pos]
        language = namespace.language

        url_caption = CAPTIONS_URL_TEMPLATE % {'lg': language, 'id': video_id}

        err, result_caption = request(http, url_caption)

        if err:
            die(err)
        elif result_caption.status >= 400:
            continue
        else:
            soup = BeautifulSoup(result_caption.data, 'lxml')
            full_text = []

            for item in soup.find_all('text'):
                full_text.append(item.get_text())

            caption_text = " ".join(full_text)

            enricher.write(line, [caption_text])


        loading_bar.update()




