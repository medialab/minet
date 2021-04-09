import csv
import sys
from tqdm import tqdm

from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import FACEBOOK_POST_CSV_HEADERS

scraper = FacebookMobileScraper(cookie='firefox')

writer = csv.writer(sys.stdout)
writer.writerow(FACEBOOK_POST_CSV_HEADERS)

loading_bar = tqdm(desc='Scraping posts', unit=' posts')

for post in scraper.posts('https://www.facebook.com/groups/186982538026569'):
    loading_bar.update()
    writer.writerow(post.as_csv_row())
