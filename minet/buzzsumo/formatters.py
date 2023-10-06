# =============================================================================
# Minet BuzzSumo Formatters
# =============================================================================
#
# Various formatters for BuzzSumo data.
#
from casanova import namedrecord

from minet.buzzsumo.constants import ARTICLES_CSV_HEADERS, EXACT_URL_HEADERS


BuzzSumoArticle = namedrecord(
    "BuzzSumoArticle",
    ARTICLES_CSV_HEADERS,
    plural=["article_amplifiers", "article_types"],
)


def format_article(data):
    keep = {}

    for k in ARTICLES_CSV_HEADERS:
        keep[k] = data[k]

    return BuzzSumoArticle(**keep)


BuzzSumoExactURL = namedrecord(
    "BuzzSumoExactURL",
    EXACT_URL_HEADERS,
    plural=["article_types"],
)


def format_exact_url(data):
    keep = {}

    for k in EXACT_URL_HEADERS:
<<<<<<< HEAD
        keep[k] = data.get(k)
=======
        keep[k] = data[k]
>>>>>>> 22b55b20 (Adding the bz exact-url command)

    return BuzzSumoExactURL(**keep)
