import csv
import sys
from tqdm import tqdm

from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import FACEBOOK_POST_CSV_HEADERS

scraper = FacebookMobileScraper(cookie='chromium')

# writer = csv.writer(sys.stdout)
# writer.writerow(FACEBOOK_POST_CSV_HEADERS)

# loading_bar = tqdm(desc='Scraping posts', unit=' posts')

# Danish: https://www.facebook.com/groups/186982538026569
# French: https://www.facebook.com/groups/444178993127747
# Langs: https://www.facebook.com/settings/?tab=language

# for post in scraper.posts('https://www.facebook.com/groups/186982538026569'):
#     loading_bar.update()
#     writer.writerow(post.as_csv_row())

scraper.group_post_user('https://www.facebook.com/groups/186982538026569')
