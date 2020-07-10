# =============================================================================
# Minet Twitter Utils
# =============================================================================
#
# Miscellaneous utility functions to be used in the twitter packages.
#
import json
from datetime import datetime
from time import sleep, time
from pytz import timezone
from twitter import Twitter, OAuth, OAuth2, TwitterHTTPError
from minet.cli.utils import print_err


class TwitterWrapper(object):

    MAX_TRYOUTS = 5

    def __init__(self, api_keys):

        self.oauth = OAuth(api_keys['access_token'], api_keys['access_token_secret'], api_keys['api_key'], api_keys['api_secret_key'])
        self.oauth2 = OAuth2(bearer_token=json.loads(Twitter(api_version=None, format="", secure=True, auth=OAuth2(api_keys['api_key'], api_keys['api_secret_key'])).oauth2.token(grant_type="client_credentials"))['access_token'])
        self.api = {
            'user': Twitter(auth=self.oauth),
            'app': Twitter(auth=self.oauth2)
        }
        self.waits = {}
        self.auth = {}

    def call(self, route, args={}, tryouts=MAX_TRYOUTS):

        if route not in self.auth:
            self.auth[route] = "user"
        auth = self.auth[route]

        try:
            return self.api[auth].__getattr__("/".join(route.split('.')))(**args)

        except TwitterHTTPError as e:
            if e.e.code == 429:
                now = time()
                reset = int(e.e.headers["x-rate-limit-reset"])

                if route not in self.waits:
                    self.waits[route] = {"user": now, "app": now}

                self.waits[route][auth] = reset
                print_err("REACHED API LIMITS on %s %s until %s for auth %s" % (route, args, reset, auth))
                minwait = sorted([(a, w) for a, w in self.waits[route].items()], key=lambda x: x[1])[0]

                if minwait[1] > now:
                    sleeptime = 5 + max(0, int(minwait[1] - now))
                    print_err("  will wait for %s for the next %ss (%s)" % (minwait[0], sleeptime, datetime.fromtimestamp(now + sleeptime).isoformat()[11:19]))
                    sleep(sleeptime)
                self.auth[route] = minwait[0]

                return self.call(route, args, tryouts)

            elif tryouts:
                return self.call(route, args, tryouts - 1)

            else:
                print_err("ERROR after %s tryouts for %s %s %s" % (self.MAX_TRYOUTS, route, auth, args))
                print_err("%s: %s" % (type(e), e))


def get_timestamp(t, locale):
    tim = datetime.strptime(t, '%a %b %d %H:%M:%S +0000 %Y')
    if locale:
        utc_date = timezone('UTC').localize(tim)
        locale_date = utc_date.astimezone(locale)
        return locale_date
    return tim.isoformat()


def clean_user_entities(user_data):
    if 'entities' in user_data:
        for k in user_data['entities']:
            if 'urls' in user_data['entities'][k]:
                for url in user_data['entities'][k]['urls']:
                    if not url['expanded_url']:
                        continue
                    if k in user_data:
                        user_data[k] = user_data[k].replace(url['url'], url['expanded_url'])
