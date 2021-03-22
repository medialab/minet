# =============================================================================
# Minet Custom Exceptions
# =============================================================================
#
# Collection of handy custom exceptions.
#


class MinetError(Exception):
    def __repr__(self):
        representation = '<' + self.__class__.__name__

        for k in dir(self):
            if (
                k.startswith('_') or
                k == 'message' or
                k == 'msg' or
                k == 'args' or
                'traceback' in k
            ):
                continue

            v = getattr(self, k)

            if isinstance(v, BaseException):
                representation += ' %s=<%s>' % (k, v.__class__.__name__)
                continue

            if isinstance(v, str):
                if len(v) > 30:
                    v = v[:29] + '…'
                v = v.replace('\n', '\\n')

            representation += ' %s="%s"' % (k, v)

        representation += '>'

        return representation


# General errors
class UnknownEncodingError(MinetError):
    pass


# Miscellaneous HTTP errors
class InvalidURLError(MinetError):
    pass


# Redirection errors
class RedirectError(MinetError):
    pass


class MaxRedirectsError(RedirectError):
    pass


class InfiniteRedirectsError(RedirectError):
    pass


class SelfRedirectError(InfiniteRedirectsError):
    pass


class InvalidRedirectError(RedirectError):
    pass


# Crawling errors
class CrawlError(MinetError):
    pass


class UnknownSpiderError(CrawlError):
    pass
