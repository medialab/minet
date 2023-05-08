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
        id = input_string.split("/")[-1]
    return id


def parse_chunk(chunk):
    for row in chunk:
        id = row[1]
        rest_of_row = row[0]
        if "," in id:
            input_list = id.split(",")
            for id in input_list:
                yield rest_of_row, id
        else:
            yield rest_of_row, id
