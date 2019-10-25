# =============================================================================
# Minet Hyphe Dump CLI Action
# =============================================================================
#
# Logic of the `hyphe dump` action.
#
import os
import csv
import base64
import zlib
import gzip
from os.path import join, dirname
from tqdm import tqdm
from datetime import datetime

from minet.utils import create_pool, md5
from minet.cli.hyphe.constants import WEBENTITY_STATUSES
from minet.cli.hyphe.utils import (
    create_corpus_jsonrpc,
    ensure_corpus_is_started
)

# Constants
BATCH_SIZE = 100


# Helpers
def count_total_webentities(stats, statuses=WEBENTITY_STATUSES):
    counts = stats['result']['corpus']['traph']['webentities']

    total = 0

    for status in statuses:
        total += counts[status]

    return total


def count_total_pages(stats):
    counts = stats['result']['corpus']['crawler']

    return counts['pages_found']


def webentities_by_status_iter(jsonrpc, status):
    token = None
    next_page = None

    while True:
        if token is None:
            err, result = jsonrpc(
                'store.get_webentities_by_status',
                status=status,
                count=BATCH_SIZE
            )
        else:
            err, result = jsonrpc(
                'store.get_webentities_page',
                pagination_token=token,
                n_page=next_page
            )

        result = result['result']

        for webentity in result['webentities']:
            yield webentity

        if 'next_page' in result and result['next_page']:
            token = result['token']
            next_page = result['next_page']
        else:
            break


def webentities_iter(jsonrpc, statuses=WEBENTITY_STATUSES):
    for status in statuses:
        yield from webentities_by_status_iter(jsonrpc, status)


def webentity_pages_iter(jsonrpc, webentity, body=False):
    token = None

    while True:
        err, result = jsonrpc(
            'store.paginate_webentity_pages',
            webentity_id=webentity['id'],
            count=BATCH_SIZE,
            pagination_token=token,
            include_page_metas=True,
            include_page_body=body
        )

        result = result['result']

        for page in result['pages']:
            yield webentity, page

        if 'token' in result and result['token']:
            token = result['token']
        else:
            break


def pages_iter(jsonrpc, webentities, body=False):
    for webentity in webentities.values():
        yield from webentity_pages_iter(jsonrpc, webentity, body=body)


WEBENTITY_HEADERS = [
    'id',
    'name',
    'status',
    'pages',
    'homepage',
    'prefixes',
    'degree',
    'undirected_degree',
    'indegree',
    'outdegree'
]


def format_webentity_for_csv(webentity):
    return [
        webentity['id'],
        webentity['name'],
        webentity['status'],
        webentity['pages_total'],
        webentity['homepage'],
        ' '.join(webentity['prefixes']),
        webentity['indegree'] + webentity['outdegree'],
        webentity['undirected_degree'],
        webentity['indegree'],
        webentity['outdegree'],
    ]


PAGE_HEADERS = [
    'url',
    'lru',
    'webentity',
    'webentity_status',
    'status',
    'crawled',
    'encoding',
    'content_type',
    'crawl_timestamp',
    'crawl_datetime',
    'size',
    'error'
]

ADDITIONAL_PAGE_HEADERS = [
    'filename'
]


def format_page_for_csv(webentity, page, filename=None, body=False):
    row = [
        page['url'],
        page['lru'],
        webentity['id'],
        webentity['status'],
        page.get('status', ''),
        '1' if page['crawled'] else '0',
        page.get('encoding', ''),
        page.get('content_type', ''),
        page['crawl_timestamp'] if 'crawl_timestamp' in page else '',
        datetime.fromtimestamp(int(page['crawl_timestamp']) / 1000).isoformat(timespec='seconds') if 'crawl_timestamp' in page else '',
        page.get('size', '') or '',
        page.get('error', '')
    ]

    if filename:
        row.append(filename)
    elif body:
        row.append('')

    return row


def format_page_filename(webentity, page):
    h = md5(page['url'])

    # TODO: could be something other than html?
    return '%s/%s/%s.html.gz' % (webentity['id'], h[:2], h)


def hyphe_dump_action(namespace):

    # Paths
    output_dir = 'hyphe_corpus_%s' % namespace.corpus

    if namespace.output_dir is not None:
        output_dir = namespace.output_dir

    os.makedirs(output_dir, exist_ok=True)

    webentities_output_path = join(output_dir, 'webentities.csv')
    pages_output_path = join(output_dir, 'pages.csv')

    if namespace.body:
        body_output_dir = join(output_dir, 'content')
        os.makedirs(body_output_dir, exist_ok=True)

    # Fixing trailing slash
    if not namespace.url.endswith('/'):
        namespace.url += '/'

    http = create_pool()
    jsonrpc = create_corpus_jsonrpc(http, namespace.url, namespace.corpus)

    # First we need to start the corpus
    ensure_corpus_is_started(jsonrpc)

    # Then we gather some handy statistics
    err, stats = jsonrpc('get_status')

    # Then we fetch webentities
    webentities_file = open(webentities_output_path, 'w')
    webentities_writer = csv.writer(webentities_file)
    webentities_writer.writerow(WEBENTITY_HEADERS)

    loading_bar = tqdm(
        desc='Paginating web entities',
        unit=' webentities',
        dynamic_ncols=True,
        total=count_total_webentities(stats)
    )

    webentities = {}

    for webentity in webentities_iter(jsonrpc):
        loading_bar.update()
        webentities[webentity['id']] = webentity
        webentities_writer.writerow(format_webentity_for_csv(webentity))

    webentities_file.close()
    loading_bar.close()

    # Finally we paginate pages
    pages_file = open(pages_output_path, 'w')
    pages_writer = csv.writer(pages_file)
    pages_writer.writerow(PAGE_HEADERS + (ADDITIONAL_PAGE_HEADERS if namespace.body else []))

    loading_bar = tqdm(
        desc='Dumping pages',
        unit=' pages',
        dynamic_ncols=True,
        total=count_total_pages(stats)
    )

    for webentity, page in pages_iter(jsonrpc, webentities, body=namespace.body):
        loading_bar.update()
        filename = None

        if namespace.body and 'body' in page:
            filename = format_page_filename(webentity, page)
            filepath = join(body_output_dir, filename)
            os.makedirs(dirname(filepath), exist_ok=True)

            with open(filepath, 'wb') as f:
                binary = base64.b64decode(page['body'])
                binary = zlib.decompress(binary)
                binary = gzip.compress(binary)

                f.write(binary)

        pages_writer.writerow(format_page_for_csv(webentity, page, filename=filename, body=namespace.body))
