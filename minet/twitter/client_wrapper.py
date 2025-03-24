# Extracted from twitwi
import json
from time import sleep, time
from operator import itemgetter
from twitter import Twitter, OAuth, OAuth2, TwitterHTTPError, Twitter2

from minet.twitter.exceptions import TwitterWrapperMaxAttemptsExceeded
from minet.twitter.constants import APP_ONLY_ROUTES

DEFAULT_MAX_ATTEMPTS = 5

# Established from: https://developer.twitter.com/en/support/twitter-api/error-troubleshooting
NO_RETRY_STATUSES = set([400, 401, 403, 404, 406, 410, 422])


class TwitterWrapper(object):
    def __init__(
        self,
        token,
        token_secret,
        consumer_key,
        consumer_secret,
        listener=None,
        api_version="1.1",
    ):
        api_version = str(api_version)

        if api_version not in ["1.1", "2"]:
            raise TypeError("API version can only be '1.1' or '2'.")

        self.oauth = OAuth(token, token_secret, consumer_key, consumer_secret)

        bearer_token_client = Twitter(
            api_version=None,
            format="",
            secure=True,
            auth=OAuth2(consumer_key, consumer_secret),
        )

        bearer_token = json.loads(
            bearer_token_client.oauth2.token(grant_type="client_credentials")
        )["access_token"]

        self.oauth2 = OAuth2(bearer_token=bearer_token)

        self.auth = {}
        self.waits = {}

        TwitterClass = Twitter

        if api_version == "2":
            TwitterClass = Twitter2

            for route in APP_ONLY_ROUTES:
                self.auth[route] = "app"
                self.waits[route] = {"app": 0}

        self.endpoints = {
            "user": TwitterClass(auth=self.oauth),
            "app": TwitterClass(auth=self.oauth2),
        }

        self.listener = listener

    def call(self, route, max_attempts=DEFAULT_MAX_ATTEMPTS, **kwargs):
        attempts = 0

        if not isinstance(route, list):
            raise TypeError(
                'twitwi.TwitterWrapper.call: expecting route as a list, such as ["friends", "ids"].'
            )

        route = "/".join(route)

        while attempts < max_attempts:
            if route not in self.auth:
                self.auth[route] = "user"

            auth = self.auth[route]

            try:
                return self.endpoints[auth].__getattr__(route)(**kwargs)

            except TwitterHTTPError as e:
                # Rate limited
                if e.e.code == 429:
                    now = int(time())

                    # If there are still API calls available, we obviously
                    # queried Twitter too fast and should just let it breathe
                    remaining = int(e.e.headers["X-Rate-Limit-Remaining"])
                    if remaining > 0:
                        attempts += 1

                        if callable(self.listener):
                            self.listener(
                                "excessive-rate",
                                {
                                    "error": e,
                                    "route": route,
                                    "attempts": attempts,
                                    "auth": auth,
                                },
                            )

                        sleep(1)
                        continue

                    reset = int(e.e.headers["X-Rate-Limit-Reset"])

                    if route not in self.waits:
                        self.waits[route] = {"user": now, "app": now}

                    self.waits[route][auth] = reset

                    if callable(self.listener):
                        self.listener(
                            "rate-limited",
                            {
                                "route": route,
                                "kwargs": kwargs,
                                "reset": reset,
                                "auth": auth,
                            },
                        )

                    min_wait = min(self.waits[route].items(), key=itemgetter(1))

                    if min_wait[1] > now:
                        sleeptime = 5 + max(0, int(min_wait[1] - now))

                        if callable(self.listener):
                            self.listener(
                                "waiting",
                                {
                                    "auth": min_wait[0],
                                    "reset": min_wait[1],
                                    "sleep": sleeptime,
                                },
                            )

                        sleep(sleeptime)

                    self.auth[route] = min_wait[0]

                    continue

                # Errors that should terminate immediately
                elif e.e.code in NO_RETRY_STATUSES:
                    raise e

                # Different error
                else:
                    attempts += 1

                    if callable(self.listener):
                        self.listener("error", {"error": e})

        raise TwitterWrapperMaxAttemptsExceeded
