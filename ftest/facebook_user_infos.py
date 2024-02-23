import csv
import sys
from tqdm import tqdm
import time
from minet.facebook import FacebookMobileScraper

scraper = FacebookMobileScraper(cookie="firefox")

USERS_URL = [
]

for url in USERS_URL:
    print(scraper.user_infos(url))