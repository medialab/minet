from minet.facebook import FacebookMobileScraper

scraper = FacebookMobileScraper("chrome")

group = scraper.group("https://www.facebook.com/groups/singingworkshopsinparis")

print(group)
