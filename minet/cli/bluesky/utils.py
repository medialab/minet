from minet.bluesky.exceptions import (
    BlueskyAuthenticationError,
    BlueskySessionRefreshError,
)

from minet.cli.utils import with_fatal_errors


def fatal_errors_hook(_, e):
    if isinstance(e, BlueskyAuthenticationError):
        return [
            "Invalid Bluesky authentication!",
            "Did you give correct information to --identifier (did you forget `.bsky.social` at the end?) and --password flags?",
            "If you don't have a password, you can create one here: [cyan]https://bsky.app/settings/app-passwords",
        ]

    if isinstance(e, BlueskySessionRefreshError):
        return ["Something went wrong when refreshing the auth session.", "Sorry :("]


def with_bluesky_fatal_errors(fn):
    return with_fatal_errors(fatal_errors_hook)(fn)
