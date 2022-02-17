from minet.twitter.api_scraper import TwitterAPIScraper

scraper = TwitterAPIScraper()

for user in scraper.search_users('maple'):
    print(user['id'], user['screen_name'])
