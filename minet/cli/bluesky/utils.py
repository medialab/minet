from minet.bluesky.exceptions import BlueskyAuthenticationError

from minet.cli.utils import with_fatal_errors


def fatal_errors_hook(_, e):
    if isinstance(e, BlueskyAuthenticationError):
        return [
            "Invalid Bluesky authentication!",
            "Did you give correct information to the --identifier (did you forget `.bsky.social` at the end?) and --password flags?",
            "If you don't have a password, you can create one here: https://bsky.app/settings/app-passwords",
        ]


def with_bluesky_fatal_errors(fn):
    return with_fatal_errors(fatal_errors_hook)(fn)
