from minet.youtube.scraper import YouTubeScraper

scraper = YouTubeScraper()

links = scraper.get_channel_links(
    "https://www.youtube.com/channel/UCHGFbA0KWBgf6gMbyUCZeCQ"
)
print(links)
