# =============================================================================
# Minet Spotify Utils
# =============================================================================
#
# General functions used throughout the Spotify functions.
#

from ural import is_url


def parse_spotify_id(input_string):
    id = input_string
    if is_url(input_string):
        id = input_string.rstrip("/").rsplit("/", 1)[-1]
    return id
