from minet.facebook import FacebookMobileScraper
from minet.cli.console import console

scraper = FacebookMobileScraper(cookie="firefox")

USERS_URL = ["https://www.facebook.com/guillaume.plique.9/"]

for url in USERS_URL:
    console.print(scraper.user_infos(url), highlight=True)
