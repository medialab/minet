from typing import Any

import warnings
from datetime import datetime
from html import unescape
from bs4 import SoupStrainer, BeautifulSoup, MarkupResemblesLocatorWarning

from .types import NamedScraper


def extract_content(content):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=MarkupResemblesLocatorWarning)
        return BeautifulSoup(unescape(content), "html.parser").get_text().strip()


def extract_date(doc_id):
    return datetime.strptime(doc_id.split("·")[1], "%Y%m%d").date().isoformat()


def extract_media(media):
    return media.split(",", 1)[0].split("\n", 1)[0].split(" " * 16, 1)[0].strip()


def select_and_strip(elem, selector):
    selected_elem = elem.select_one(selector)

    if selected_elem is None:
        return ""

    return selected_elem.get_text().strip()


class EuropresseScraper(NamedScraper):
    name = "europresse"
    fieldnames = ["id", "title", "content", "url", "date", "media", "media_id"]
    plural = True
    output_type = "collection"
    strainer = SoupStrainer(name="article")

    def scrape(self, soup: BeautifulSoup, context=None) -> Any:
        articles = []
        selectors = {
            "title": ".titreArticle",
            "id": ".publiC-lblNodoc",
            "media": ".DocPublicationName",
        }

        for elem in soup.select("article"):
            row = {}

            content = elem.select_one(".docOcurrContainer")
            if content is None:
                content = ""
            else:
                urls = content.select("a")
                for u in urls:
                    if "Cet article est paru dans" in u.get_text():
                        row["url"] = u.get("href")
                        break
                content = content.get_text()

            row["content"] = extract_content(content)

            for field, selector in selectors.items():
                row[field] = select_and_strip(elem, selector)

            row["date"] = extract_date(row["id"])
            row["media"] = extract_media(row["media"])
            row["media_id"] = row["id"].split("·")[2]

            articles.append(row)

        return articles
