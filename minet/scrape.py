# =============================================================================
# Minet Scrape Function
# =============================================================================
#
# Function interpreting minet's scraping JSON descriptive DSL format to
# actually scrape content off of HTML content.
#
from bs4 import BeautifulSoup


def scrape(html, specs):
    soup = BeautifulSoup(html, 'lxml')

    if specs['iterator']:
        for element in soup.select(specs['iterator']):
            yield element.get_text()
