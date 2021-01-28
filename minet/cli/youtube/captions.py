# =============================================================================
# Minet Youtube Captions CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving caption about
# the given Youtube videos.
#
from bs4 import BeautifulSoup
from tqdm import tqdm
from minet.cli.utils import print_err
from urllib.parse import unquote
import casanova
import time
import re
import json
from minet.utils import create_pool, request

get_info = re.compile(r'({"captionTracks":.*isTranslatable":(true|false)}])')
timed = re.compile('timedtext?[^"]+')

REPORT_HEADERS = [
    'caption_text'
]

INFO_URL_TEMPLATE = 'https://www.youtube.com/get_video_info?video_id=%(id)s'
VIDEO_CALL_TEMPLATE = 'https://www.youtube.com/watch?v=%(id)s'
API_BASE_URL = 'https://www.youtube.com/api/%(temp)s'


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
        url_caption = ''
        url_inf = INFO_URL_TEMPLATE % {'id': video_id}
        err1, info_vid = request(http, url_inf)
        info_vid_dec = unquote(str(info_vid.data))
        captionsTracks = re.findall(get_info, info_vid_dec)
        if captionsTracks:
            dict_captions = json.loads(captionsTracks[0][0] + '}')['captionTracks']
            for i in range(len(dict_captions)):
                if namespace.lang and namespace.lang == dict_captions[i]['languageCode']:
                    url_caption = dict_captions[i]['baseUrl']
                    break
            if not(url_caption) and dict_captions:
                url_caption = dict_captions[0]['baseUrl']

        else:
            url_vid = VIDEO_CALL_TEMPLATE % {'id': video_id}
            urls = []
            time.sleep(0.01)
            err, result = request(http, url_vid)
            timedtext = re.findall(timed, str(result.data))
            for x in timedtext:
                proper_timed = x.replace("\\\\u0026", "&")
                if proper_timed[-2:] == namespace.lang:
                    url_caption = API_BASE_URL % {'temp': proper_timed}
                    break
            if not(url_caption) and timedtext and not(namespace.lang):
                url_caption = API_BASE_URL % {'temp': timedtext[1].replace("\\\\u0026", "&")}
        if not url_caption:
            print_err('no subtitles for {}'.format(video_id))
            continue

        time.sleep(0.01)
        err, result_caption = request(http, url_caption)

        if err is not None:
            print_err(err)
        elif result_caption.status >= 400:
            print_err(f'error, status : {result_caption.status} for id : {video_id}')
            enricher.writerow(line)
        else:
            soup = BeautifulSoup(result_caption.data, 'lxml')

            full_text = []

            caption_text = " ".join(item.get_text() for item in soup.find_all('text'))

            enricher.writerow(line, [caption_text])

        loading_bar.update()
