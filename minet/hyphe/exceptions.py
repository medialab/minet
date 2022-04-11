# =============================================================================
# Minet Hyphe Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class HypheError(MinetError):
    pass


class HypheJSONRPCError(HypheError):
    def __init__(self, payload):
        super().__init__(payload["faultString"])
        self.code = payload["faultCode"]
        self.fault = payload["fault"]

    def __str__(self):
        return super().__str__() + ", Code: %i, Fault: %s" % (self.code, self.fault)


class HypheRequestFailError(HypheError):
    pass


class HypheCorpusAuthenticationError(HypheError):
    pass


class HypheCouldNotStartCorpusError(HypheError):
    pass
