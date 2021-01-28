from minet.twitter.api_scraper import TwitterAPIScraper

scraper = TwitterAPIScraper()
scraper.acquire_guest_token()
print(scraper.guest_token)
