import calendar
import dateparser
from datetime import datetime


def timestamp_to_isoformat(timestamp):
    return datetime.utcfromtimestamp(timestamp).isoformat()


def parse_date(formatted_date, lang="en"):
    if not isinstance(formatted_date, str):
        raise TypeError

    parsed = dateparser.parse(formatted_date, languages=[lang])

    if not parsed:
        return None

    return parsed.isoformat().split(".", 1)[0]


PARTIAL_ISO_FORMATS = {
    4: (r"%Y", "year"),
    7: (r"%Y-%m", "month"),
    10: (r"%Y-%m-%d", "day"),
    13: (r"%Y-%m-%dT%H", "hour"),
    16: (r"%Y-%m-%dT%H:%M", "minute"),
    19: (r"%Y-%m-%dT%H:%M:%S", "second"),
    20: (r"%Y-%m-%dT%H:%M:%SZ", "second"),
}


def datetime_from_partial_iso_format(
    string: str, upper_bound: bool = False
) -> datetime:
    try:
        possible_date_format, precision = PARTIAL_ISO_FORMATS[len(string)]
    except KeyError:
        raise ValueError("cannot parse date {!r}".format(string))

    result = datetime.strptime(string, possible_date_format)

    if upper_bound:
        if precision == "year":
            result = result.replace(month=12, day=31, hour=23, minute=59, second=59)
        elif precision == "month":
            _, last_day = calendar.monthrange(result.year, result.month)
            result = result.replace(day=last_day, hour=23, minute=59, second=59)
        elif precision == "day":
            result = result.replace(hour=23, minute=59, second=59)
        elif precision == "hour":
            result = result.replace(minute=59, second=59)
        elif precision == "minute":
            result = result.replace(second=59)

    return result
