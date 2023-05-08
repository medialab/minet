# =============================================================================
# Minet Spotify API Client
# =============================================================================
#
# A handy API client used by the CLI actions.
#
import time
import json

from minet.spotify.constants import BASE_API_ENDPOINT_V1
from minet.web import create_request_retryer, request, retrying_method
from minet.spotify.exceptions import SpotifyAPIError
from ural.format_url import URLFormatter

LIMIT = 50


def get_access_token(client_id: str, client_secret: str):
    response = request(
        url="https://accounts.spotify.com/api/token",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}",
    )
    if response.is_text:
        try:
            response_body = response.json()
        except Exception:
            raise json.decoder.JSONDecodeError(
                msg=f"Mal formatted response from Spotify API.\n{response.text()}\n",
                doc=response.text(),
                pos=0,
            )
        access_token = response_body.get("access_token")
        if not access_token:
            raise KeyError("Response missing access token.")
        else:
            return access_token


class SpotifyAPIClient(object):
    def __init__(self, client_id, client_secret):
        self.access_token = get_access_token(
            client_id=client_id, client_secret=client_secret
        )
        self.retryer = create_request_retryer()
        self.spotify_url = URLFormatter(base_url=BASE_API_ENDPOINT_V1)

    @retrying_method()
    def request_json(self, url):
        response = request(
            url=url, headers={"Authorization": f"Bearer {self.access_token}"}
        )
        if response.status == 429:
            time.sleep(30)
            response = request(
                url=url, headers={"Authorization": f"Bearer {self.access_token}"}
            )
        elif response.status != 200:
            raise SpotifyAPIError(response.text(), url, response.status)
        return response.json()

    def search(self, query, type, market, method):
        search_args = {"q": query, "type": type, "market": market, "limit": LIMIT}
        url = self.spotify_url.format(path="search", args=search_args)
        return self.generator(base_url=url, formatter=method, do_offset=True)

    def get_by_id(self, ids, type, market, method):
        path = type
        args = {"market": market, "limit": LIMIT}
        url = self.spotify_url.format(path=path, args=args)
        # Temporary fix for formatted string of IDs
        id_string = "%2C".join(ids)
        url += "&ids=" + id_string
        return self.generator(base_url=url, formatter=method, do_offset=False)

    def get_episodes_by_show_id(self, id, market, method):
        path = f"shows/{id}/episodes"
        args = {"market": market, "limit": LIMIT}
        url = self.spotify_url.format(path=path, args=args)
        return self.generator(base_url=url, formatter=method, do_offset=True)

    def generator(self, base_url, formatter, do_offset):
        go_to_next_page = True
        offset = 0
        while go_to_next_page:
            # If the request type doesn't require offsetting to the next page,
            # (i.e. it is requesting by ID) do not continue after client call
            if not do_offset:
                go_to_next_page = False

            # Update the URL with an offset if necessary
            url = base_url + "&offset=" + str(offset)
            result = self.request_json(url)
            offset += LIMIT

            # Get an array of the target data
            items = []
            if result.get("items"):
                items = result["items"]
            elif len(list(result.keys())) == 1:
                data_type = list(result.keys())[0]
                result = result[data_type]
                if isinstance(result, dict):
                    items = result.get("items")
                elif isinstance(result, list):
                    items = result

            # Yield each item in the array of target data
            if isinstance(items, list) and len(items) > 0:
                for item in items:
                    if not item:
                        raise SpotifyAPIError(response=result, url=url)
                    else:
                        formatted_item = formatter(item)
                        yield formatted_item
            # If there are no more items in the returned array, do not continue
            else:
                go_to_next_page = False
