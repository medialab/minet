# =============================================================================
# Minet Mediacloud Utils
# =============================================================================
#
# Miscellaneous utility function used throughout the mediacloud package.
#


def get_next_link_id(data):

    if 'link_ids' not in data:
        return None

    pagination = data['link_ids']

    if not pagination.get('next'):
        return None

    return pagination['next']
