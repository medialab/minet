# =============================================================================
# Minet Spotify API Client
# =============================================================================
#
# A handy API client used by the CLI actions.
#
import json

from minet.spotify.constants import BASE_API_ENDPOINT_V1
from minet.web import create_request_retryer, request, retrying_method
from minet.spotify.formatters import format_show, format_episode
import time

def get_access_token(client_id:str, client_secret:str):
    response = request(
        url='https://accounts.spotify.com/api/token',
        method='POST',
        headers={'Content-Type':'application/x-www-form-urlencoded'},
        body=f'grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}'
    )
    if response.is_text:
        try:
            response_body = response.json()
        except Exception:
            raise json.decoder.JSONDecodeError(
                msg=f'Mal formatted response from Spotify API.\n{response.text()}\n',
                doc=response.text(),
                pos=0
            )
        access_token = response_body.get('access_token')
        if not access_token:
            raise KeyError('Response missing access token.')
        else:
            return access_token


def forge_search_url(search_kwargs):
    if search_kwargs.get('q'):
        q = '%20'.join(search_kwargs['q'].split())
        q = '%3'.join(q.split(':'))
        search_kwargs['q'] = q
    search_kwargs.update({"limit":50})
    args = [f'{k}={v}' for k,v in search_kwargs.items() if v]
    query = '&'.join(args)
    return BASE_API_ENDPOINT_V1+'search?'+query


class SpotifyAPIClient(object):
    def __init__(self, client_id, client_secret, kwargs):
        self.access_token = get_access_token(
            client_id=client_id,
            client_secret=client_secret
        )
        self.retryer = create_request_retryer()
        self.cli_search_kwargs = kwargs

    @retrying_method()
    def request_json(self, url):
        response = request(
            url=url,
            headers={'Authorization':f'Bearer {self.access_token}'}
        )
        if response.status == 429:
            time.sleep(30)
            response = request(
                url=url,
                headers={'Authorization':f'Bearer {self.access_token}'}
            )
        elif response.status != 200:
            print(response.text())
            raise KeyError
        return response.json()

    def shows(self, query):
        search_kwargs = {"q":query, "type":"show"}
        search_kwargs.update(self.cli_search_kwargs)
        url = forge_search_url(search_kwargs)
        return self.generator(url, format_show)

    def episodes(self, query):
        search_kwargs = {"q":query, "type":"episode"}
        search_kwargs.update(self.cli_search_kwargs)
        url = forge_search_url(search_kwargs)
        return self.generator(url, format_episode)

    def generator(self, url, formatter):
        go_to_next_page = True
        while go_to_next_page:
            result = self.request_json(url)
            # If the result doesn't declare a type
            if result.get("items"):
                data = result
            # Or if the result declares the media type
            elif len(list(result.keys())) == 1:
                type = list(result.keys())[0]
                data = result[type]
            else:
                raise KeyError
            # Determine the next results page
            url = data.get("next")
            if not url:
                go_to_next_page = False
            # Yield results in the items array
            items = data.get("items")
            if isinstance(items, list) and len(items) > 0:
                for item in items:
                    formatted_item = formatter(item)
                    yield formatted_item
            else :
                go_to_next_page = False
