# =============================================================================
# Minet BuzzSumo Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the BuzzSumo namespace.
#
from datetime import datetime

from minet.cli.utils import die


FIVE_YEARS_IN_SEC = 5 * 365.25 * 24 * 60 * 60


def convert_string_date_into_timestamp(string_date):

    try:
        timestamp = datetime.strptime(string_date, '%Y-%m-%d').timestamp()
    except ValueError:
        die(['"%s" is an incorrect date format, it should be "YYYY-MM-DD" (eg: "2021-12-31").' % string_date])

    if (datetime.now().timestamp() - timestamp) > FIVE_YEARS_IN_SEC:
        die(['You cannot query BuzzSumo using dates before 5 years ago, please change "%s" into a later date.' % string_date])

    return timestamp
