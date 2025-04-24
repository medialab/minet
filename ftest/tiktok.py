from minet.cli.utils import get_rcfile
from minet.cli.console import console

from minet.tiktok import TikTokHTTPClient

conf = get_rcfile()
assert conf is not None

client = TikTokHTTPClient(conf["tiktok"]["api_key"], conf["tiktok"]["api_secret"])

start_date = "20241001"
end_date = "20241002"
country = "RO"
max_results = 10

for content in client.search_commercial_contents(
    country_code=country,
    start_date=start_date,
    end_date=end_date,
    max_results=max_results,
):
    console.print(content, highlight=True)
