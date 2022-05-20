import csv
from minet.instagram import InstagramAPIScraper

scraper = InstagramAPIScraper(cookie="chrome")

# QUERY = 'shawarmaorlando'
# QUERY = 'eurorack'
QUERY = "climatehoax"

with open("./posts.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["id"])

    for shortcode in scraper.search_hashtag(QUERY):
        writer.writerow([shortcode])
