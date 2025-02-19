from minet.exceptions import MinetError


class BlueskyError(MinetError):
    pass


class BlueskyAuthenticationError(BlueskyError):
    pass


class BlueskySessionRefreshError(BlueskyError):
    pass
