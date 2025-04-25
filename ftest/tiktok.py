from minet.cli.utils import get_rcfile
from minet.cli.console import console

from minet.tiktok import TikTokHTTPClient, TiktokAPIScraper

conf = get_rcfile()
assert conf is not None

# client = TikTokHTTPClient(conf["tiktok"]["api_key"], conf["tiktok"]["api_secret"])
client = TiktokAPIScraper()

start_date = "20241001"
end_date = "20241002"
country = "RO"
max_results = 10

for content in client.search_commercial_contents(
    country=country,
    min_date=1664575200,
    max_date=1745590397,
):
    console.print(content, highlight=True)
