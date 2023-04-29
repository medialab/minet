# =============================================================================
# Minet Spotify Constants
# =============================================================================
#
# General constants used throughout the Spotify functions.
#

BASE_API_ENDPOINT_V1 = 'https://api.spotify.com/v1/'

SPOTIFY_EPISODE_HEADERS = [
        'id',
        'type',
        'name',
        'release_date',
        'release_date_precision',
        'language',
        'languages',
        'duration',
        'explicit',
        'description',
        'html_description',
        'url'
    ]

SPOTIFY_SHOW_HEADERS = [
        'id',
        'type',
        'name',
        'total_episodes',
        'publisher',
        'description',
        'html_description',
        'explicit',
        'languages',
        'available_markets',
        'url'
    ]