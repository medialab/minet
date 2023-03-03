from minet.exceptions import MinetError


class WikipediaError(MinetError):
    pass


class WikimediaRESTAPIError(WikipediaError):
    pass


class WikimediaRESTAPIThrottledError(WikimediaRESTAPIError):
    pass


class WikimediaRESTAPIServerError(WikimediaRESTAPIError):
    pass
