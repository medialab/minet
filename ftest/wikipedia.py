from minet.wikipedia import WikimediaRestAPIClient
from minet.cli.console import console

client = WikimediaRestAPIClient()

names = ["Barack_Obama", "Johann_Wolfgang_von_Goethe"]

for name, pageviews in client.pageviews(
    names,
    lang="en",
    start_date="2015100100",
    end_date="2015103100",
    granularity="daily",
):
    console.print(name, pageviews, highlight=True)
