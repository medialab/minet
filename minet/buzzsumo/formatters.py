# =============================================================================
# Minet BuzzSumo Formatters
# =============================================================================
#
# Various formatters for BuzzSumo data.
#
from casanova import namedrecord

from minet.buzzsumo.constants import ARTICLES_CSV_HEADERS


BuzzSumoArticle = namedrecord(
    'BuzzSumoArticle',
    ARTICLES_CSV_HEADERS,
    plural=['article_amplifiers', 'article_types']
)


def format_article(data):
    keep = {}

    for k in ARTICLES_CSV_HEADERS:
        keep[k] = data[k]

    return BuzzSumoArticle(**keep)
