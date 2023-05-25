from minet.crawl import Crawler, CrawlJob, CrawlResult
from minet.crawl.focus import FocusSpider
from minet.cli.console import console

import os.path
import csv
import hashlib
import collections
import sys
import ural
import urllib.parse

# Experimental class

def test(spider, path, keep_uninteresting = False):
    storage_path = os.path.join(path, "store")
    export_path = os.path.join(path, "results.csv")
    queue_path = os.path.join(storage_path, "queue")
    cache_path = os.path.join(storage_path, "urls")

    os.makedirs(path, exist_ok=True)
    os.makedirs(storage_path, exist_ok=True)
    os.makedirs(queue_path, exist_ok=True)
    os.makedirs(cache_path, exist_ok=True)

    #print(storage_path)
    with open(export_path, "a") as file:
        with Crawler(
            spider,
            throttle=0.0,
            persistent_storage_path=storage_path,
            domain_parallelism=5,
            visit_urls_only_once=True,
            normalized_url_cache=True,
            resume=True) as crawler:

            headers = CrawlResult.FIELDNAMES + ["interesting"]

            writer = csv.DictWriter(file, headers)
            writer.writeheader()

            for result in crawler:

                focus_rep: FocusSpider.FocusResponse = result.data

                print(
                    f"Depth : {result.job.depth} | Reste : {crawler.queue.qsize()} | Error : {result.error}"
                )

                if not focus_rep: continue
                if not focus_rep.interesting: continue

                row = result.as_csv_row() + [focus_rep.interesting]
                writer.writerow({headers[i] : row[i] for i in range(len(row))})



SPIDER_WIKIPEDIA = FocusSpider(
    ["https://fr.wikipedia.org/wiki/Automatisation_de_la_ligne_1_du_m%C3%A9tro_de_Paris"],
    4,
    keywords=["métro", "automatisation", "RATP"],
    regex_content=False,
    regex_url="^fr\.wikipedia\.org\/wiki\/[^:?#]+$"
)

SPIDER_RSS = FocusSpider(
    ["https://radiofrance.fr/"],
    5,
    regex_content="<rss.*version.*>",
    regex_url="radiofrance",
    perform_on_html=True,
    stop_when_not_interesting=False
)


#test(SPIDER_RSS, "../results/focus-rss/focus_rss.csv", "/Users/cesar/Documents/Medialab/results/focus-rss/db")


SPIDER_RETRAITES_TXT = FocusSpider(
    ["https://fr.wikipedia.org/wiki/R%C3%A9forme_des_retraites_en_France_en_2023"],
    3,
    regex_content="(?=.*[Rr]éform)(?=.*[Rr]etraite)",
    only_target_html_page=True,
    stop_when_not_interesting=False,
    perform_on_html=False

)

SPIDER_RETRAITES_HTML = FocusSpider(
    ["https://fr.wikipedia.org/wiki/R%C3%A9forme_des_retraites_en_France_en_2023"],
    3,
    regex_content="(?=.*[Rr]éform)(?=.*[Rr]etraite)",
    only_target_html_page=True,
    stop_when_not_interesting=False,
    perform_on_html=True

)

#test(SPIDER_RETRAITES, "../results/focus-retraites/output_txt")

test(SPIDER_RETRAITES_HTML, "../results/focus-retraites/output_html")
