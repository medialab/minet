from minet.facebook import FacebookMobileScraper

scraper = FacebookMobileScraper("chrome")

group = scraper.group("GIVE URL")

print(group)
