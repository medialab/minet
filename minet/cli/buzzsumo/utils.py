from argparse import ArgumentTypeError
from datetime import datetime

FIVE_YEARS_IN_SEC = 5 * 365.25 * 24 * 60 * 60


class BuzzSumoDateType(object):
    def __call__(self, date):
        try:
            timestamp = int(datetime.strptime(date, "%Y-%m-%d").timestamp())
        except ValueError:
            raise ArgumentTypeError(
                "dates should have the following format : YYYY-MM-DD."
            )

        if (datetime.now().timestamp() - timestamp) > FIVE_YEARS_IN_SEC:
            raise ArgumentTypeError(
                "you cannot query BuzzSumo using dates before 5 years ago."
            )

        return timestamp
