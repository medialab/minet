from minet.crawl import Crawler, CrawlJob
from minet.crawl.focus import FocusSpider
from minet.cli.console import console

import csv
import hashlib
import collections
import sys
import ural
import urllib.parse

FOCUS_SPIDER = FocusSpider(
    ["https://fr.wikipedia.org/wiki/Automatisation_de_la_ligne_1_du_m%C3%A9tro_de_Paris"],
    4,
    keywords=["métro", "automatisation", "RATP"],
    regex_content=False,
    regex_url="^fr\.wikipedia\.org\/wiki\/[^:?#]+$"
)

PARENT_URL = collections.defaultdict(str)

COUNTER = 0

def hash(str):
    try:
        hash = hashlib.md5(str.encode()).hexdigest()
    except:
        print(f"Aie : {str}")
        hash = ""
    finally:
        return hash

TREATED_SET = set()

with open("../metro_auto.csv", "w") as file:
    with Crawler(FOCUS_SPIDER, throttle=0.0, domain_parallelism=5, visit_urls_only_once=True) as crawler:
        ignored_url_set = set()

        headers = ["url", "depth", "visited", "interesting", "parent url"]

        writer = csv.DictWriter(file, headers)
        writer.writeheader()

        for result in crawler:
            focus_response: FocusSpider.FocusResponse = result.data
            if not focus_response: continue

            final_url = ural.normalize_url(urllib.parse.unquote(result.response.end_url))

            #print(final_url)

            interesting = focus_response.interesting
            i_urls = focus_response.ignored_url
            ok_urls = focus_response.next_urls

            row = [
                final_url,
                result.job.depth,
                True,
                interesting,
                PARENT_URL[final_url]
            ]



            writer.writerow({headers[i] : row[i] for i in range(len(row))})

            """
            for a in i_urls:
                if (a, final_url) in TREATED_SET: continue
                row = [
                    a,
                    result.job.depth + 1,
                    False,
                    False,
                    final_url
                ]

                TREATED_SET.add((a, final_url))

                writer.writerow({headers[i] : row[i] for i in range(len(row))})
            """

            for a in ok_urls:
                if not PARENT_URL[a]:
                    PARENT_URL[a] = final_url


            #sys.stderr.write(f"Depth : {result.job.depth} | Nb next : {len(focus_response.next_urls)} | Reste : {crawler.queue.qsize()}\n")


