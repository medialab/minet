from typing import Any

import locale
import warnings
from datetime import datetime
from html import unescape
from bs4 import SoupStrainer, BeautifulSoup, MarkupResemblesLocatorWarning

from .types import NamedScraper

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

DAYS_OF_WEEK_FR = [
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
]

DAYS_OF_WEEK_EN = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def extract_date(doc_header):
    date = ""
    date_index = 0
    found_date = False
    doc_header_list = doc_header.split(" ")

    for enum, word in enumerate(doc_header_list):
        if word.lower() in DAYS_OF_WEEK_FR:
            found_date = True
            date_index = enum
            loc = locale.setlocale(locale.LC_ALL, "fr_FR.utf8")
        elif word.strip(",").lower() in DAYS_OF_WEEK_EN:
            found_date = True
            date_index = enum
            loc = locale.setlocale(locale.LC_ALL, "en_US.utf8")

        if found_date:
            if enum in range(date_index, date_index + 3):
                date += word + " "

            elif enum == date_index + 3:
                date += word

                try:
                    if loc[:2] == "fr":
                        formatted_date = datetime.strptime(date, "%A %d %B %Y")
                    else:
                        formatted_date = datetime.strptime(date, "%A, %B %d, %Y")

                    return formatted_date.date().isoformat()

                except ValueError:
                    return extract_date(" ".join(doc_header_list[enum:]))


def select_and_strip(elem, selector):
    selected_elem = elem.select_one(selector)

    if selected_elem is None:
        return ""

    return selected_elem.get_text().strip()


class EuropresseScraper(NamedScraper):
    name = "europresse"
    fieldnames = ["id", "title", "content", "url", "date", "media"]
    plural = True
    output_type = "collection"
    strainer = SoupStrainer(name="article")

    def scrape(self, soup: BeautifulSoup, context=None) -> Any:
        articles = []
        selectors = {
            "title": ".titreArticle",
            "id": ".publiC-lblNodoc",
            "date": ".DocHeader",
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

            for field, selector in selectors.items():
                row[field] = select_and_strip(elem, selector)

            row["content"] = (
                BeautifulSoup(unescape(content), "html.parser").get_text().strip()
            )
            row["date"] = extract_date(row["date"])
            row["media"] = (
                row["media"]
                .split(",", 1)[0]
                .split("\n", 1)[0]
                .split(" " * 16, 1)[0]
                .strip()
            )

            articles.append(row)

        return articles
