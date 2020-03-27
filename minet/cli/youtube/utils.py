# =============================================================================
# Minet Youtube CLI Utils
# =============================================================================
#
# Miscellaneous helper functions related to Youtube API.
#

from pytz import timezone
from datetime import datetime


def seconds_to_midnight_pacific_time():
    now_utc = timezone('utc').localize(datetime.utcnow())
    pacific_time = now_utc.astimezone(timezone('US/Pacific')).replace(tzinfo=None)
    midnight_pacific = datetime.combine(pacific_time, datetime.min.time())
    return (midnight_pacific - pacific_time).seconds
