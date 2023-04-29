# =============================================================================
# Minet Spotify Formatters
# =============================================================================
#
# Various data formatters for Spotify data.
#

from casanova import namedrecord

from minet.spotify.constants import (SPOTIFY_EPISODE_HEADERS,
                                     SPOTIFY_SHOW_HEADERS)

ShowRecord = namedrecord(
    name='ShowRecord',
    fields=SPOTIFY_SHOW_HEADERS,
    defaults=[None for _ in range(len(SPOTIFY_SHOW_HEADERS))]
)


def format_show(item:dict) -> list:
    return ShowRecord(
        id = item.get('id'),
        type = item.get('type'),
        name = item.get('name'),
        publisher = item.get('publisher'),
        description = item.get('description'),
        html_description = item.get('html_description'),
        explicit = item.get('explicit'),
        languages = item.get('languages'),
        total_episodes = item.get('total_episodes'),
        available_markets = item.get('available_markets'),
        url = item.get('external_urls',{}).get('spotify')
    )


EpisodeRecord = namedrecord(
    name='EpisodeRecord',
    fields=SPOTIFY_EPISODE_HEADERS,
    defaults=[None for _ in range(len(SPOTIFY_EPISODE_HEADERS))]
)


def format_episode(item:dict):
    return EpisodeRecord(
        id = item.get('id'),
        type = item.get('type'),
        name = item.get('name'),
        release_date = item.get('release_date'),
        release_date_precision = item.get('release_date_precision'),
        language = item.get('language'),
        languages = item.get('languages'),
        duration = item.get('duration'),
        explicit = item.get('explicit'),
        description = item.get('description'),
        html_description = item.get('html_description'),
        url = item.get('external_urls',{}).get('spotify')
    )
