from minet.facebook import FacebookMobileScraper

scraper = FacebookMobileScraper("chrome")

group = scraper.group_or_page("https://www.facebook.com/43950390612955")

print(group)
