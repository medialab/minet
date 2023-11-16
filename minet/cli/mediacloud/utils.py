from minet.cli.utils import with_fatal_errors

from minet.mediacloud.exceptions import MediacloudServerError


def fatal_errors_hook(_, e):
    if isinstance(e, MediacloudServerError):
        return ["Aborted due to a mediacloud server error:", e.server_error]


def with_mediacloud_fatal_errors(fn):
    return with_fatal_errors(fatal_errors_hook)(fn)
