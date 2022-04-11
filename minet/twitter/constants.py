# =============================================================================
# Minet Twitter Constants
# =============================================================================
#
# General constants used throughout the Twitter functions.
#
from urllib3 import Timeout


TWITTER_PUBLIC_API_DEFAULT_TIMEOUT = Timeout(connect=10, read=60 * 2)
TWITTER_PUBLIC_API_AUTH_HEADER = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

TWITTER_API_MAX_STATUSES_COUNT = 200

ADDITIONAL_TWEET_FIELDS = ["intervention_type", "intervention_text", "intervention_url"]
