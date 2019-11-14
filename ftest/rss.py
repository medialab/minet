import csv
from minet import crawl
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def process(job, response, content, meta):
    soup = BeautifulSoup(content, 'lxml')

    links = soup.select('link[type="application/rss+xml"], link[type="application/atom+xml"]')

    rss = [urljoin(response.geturl(), link.get('href')) for link in links]

    return None, rss

with open('./ftest/resources/medias.csv') as f:
    reader = csv.reader(f)
    next(reader)

    urls = (line[0] for line in reader)

    for result in crawl(spider=process, start_jobs=urls):
        print(result.scraped)
