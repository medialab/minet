from minet.cli.utils import get_rcfile
from minet.cli.console import console

from minet.tiktok import TiktokHTTPClient, TiktokAPIScraper

conf = get_rcfile()
assert conf is not None

client = TiktokHTTPClient(conf["tiktok"]["api_key"], conf["tiktok"]["api_secret"])
# client = TiktokAPIScraper()

start_date = "20241001"
end_date = "20241002"
country = "RO"
max_results = 10

for content in client.search_commercial_contents(
    country=country,
    min_date=start_date,
    max_date=end_date,
):
    console.print(content, highlight=True)
