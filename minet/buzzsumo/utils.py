# =============================================================================
# Minet BuzzSumo Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the BuzzSumo namespace.
#
from datetime import datetime


def convert_string_date_into_timestamp(date):
    return datetime.strptime(date, '%Y-%m-%d').timestamp()
