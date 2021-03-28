# =============================================================================
# Minet Scrapers Standard Library
# =============================================================================
#
# Collection of helpers, and depencies exposed to scraper evaluation.
#
import re
import json
import soupsieve
import dateparser
from urllib.parse import urljoin


def parse_date(formatted_date, lang='en'):
    try:
        parsed = dateparser.parse(
            formatted_date,
            languages=[lang]
        )
    except ValueError:
        return None

    return parsed.isoformat().split('.', 1)[0]


def get_default_evaluation_context():
    return {

        # Dependencies
        'json': json,
        'urljoin': urljoin,
        're': re,
        'soupsieve': soupsieve,

        # Helpers
        'parse_date': parse_date
    }
