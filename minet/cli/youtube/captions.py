# =============================================================================
# Minet Youtube Captions CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving caption about
# the given Youtube videos.
#
import casanova
from bs4 import BeautifulSoup
from tqdm import tqdm
from minet.cli.utils import print_err
from minet.utils import create_pool, request

REPORT_HEADERS = [
    'caption_text'
]

CAPTIONS_URL_TEMPLATE = 'https://www.youtube.com/api/timedtext?lang=%(lang)s&v=%(id)s'


def captions_action(namespace, output_file):

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=REPORT_HEADERS
    )

    loading_bar = tqdm(
        desc='Retrieving',
        dynamic_ncols=True,
        unit=' videos',
    )

    http = create_pool()

    for line, video_id in enricher.cells(namespace.column, with_rows=True):
        url_caption = CAPTIONS_URL_TEMPLATE % {'lang': namespace.lang, 'id': video_id}

        err, result_caption = request(http, url_caption)

        if err is not None:
            raise err
        elif result_caption.status >= 400:
            print_err('request error %s' % result_caption.status)
            enricher.writerow(line)
        else:
            soup = BeautifulSoup(result_caption.data, 'lxml')
            full_text = []

            caption_text = " ".join(item.get_text() for item in soup.find_all('text'))

            enricher.writerow(line, [caption_text])

        loading_bar.update()
