from minet.facebook.emulated_scraper import FacebookEmulatedScraper

with FacebookEmulatedScraper() as scraper:
    scraper.scrape_comments(
        "https://www.facebook.com/brazzanews/posts/pfbid0365frvtkKdKVfCwcktAEPt3sNinRfcnGDEPgpTEj1vtF7KvozPmqMWpzF8Pbggnznl"
    )
