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


def explode_tags(data, join_char=None):
    tags = []
    tag_sets = []
    tags_ids = []
    tag_sets_ids = []

    for tag in data:
        tags.append(tag['tag'])
        tag_sets.append(tag['tag_set'])
        tags_ids.append(tag['tags_id'])
        tag_sets_ids.append(tag['tag_sets_id'])

    if join_char is not None:
        tags = join_char.join(tags)
        tag_sets = join_char.join(tag_sets)
        tags_ids = join_char.join(str(i) for i in tags_ids)
        tag_sets_ids = join_char.join(str(i) for i in tag_sets_ids)

    return tags, tag_sets, tags_ids, tag_sets_ids


def get_last_processed_stories_id(data):
    if not data:
        return None

    return data[-1]['processed_stories_id']
