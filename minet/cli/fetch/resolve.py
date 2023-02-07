from minet.cli.fetch.fetch import action as fetch_action


def action(*args, **kwargs):
    return fetch_action(*args, resolve=True, **kwargs)
