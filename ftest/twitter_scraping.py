from minet.cli.console import console

# from minet.twitter import TwitterAPIScraper

# scraper = TwitterAPIScraper("firefox")

# for user in scraper.followers_you_know("794083798912827393"):
#     print(user)

from minet.twitter import TwitterGuestAPIScraper

scraper = TwitterGuestAPIScraper()
tweet = scraper.tweet("1747650538865311986")

console.print(tweet, highlight=True)
