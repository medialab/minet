from minet.cli.console import console
from minet.facebook.emulated_scraper import FacebookEmulatedScraper

with FacebookEmulatedScraper(headless=False) as scraper:
    comments = scraper.scrape_comments(
        "https://www.facebook.com/brazzanews/posts/pfbid0365frvtkKdKVfCwcktAEPt3sNinRfcnGDEPgpTEj1vtF7KvozPmqMWpzF8Pbggnznl"
    )

    for comment in comments:
        console.print(comment, highlight=True)
