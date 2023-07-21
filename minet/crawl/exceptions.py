from minet.exceptions import MinetError


class CrawlerError(MinetError):
    pass


class CrawlerAlreadyFinishedError(CrawlerError):
    pass
