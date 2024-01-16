from minet.twitter import TwitterAPIScraper

scraper = TwitterAPIScraper("firefox")

for user in scraper.followers_you_know("794083798912827393"):
    print(user)
