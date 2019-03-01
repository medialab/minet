# =============================================================================
# Minet Scrape Function
# =============================================================================
#
# Function interpreting minet's scraping JSON descriptive DSL format to
# actually scrape content off of HTML content.
#
from bs4 import BeautifulSoup


def scrape_from_soup(soup, specs):

    item_specs = specs.get('item')

    if specs['iterator']:
        for element in soup.select(specs['iterator']):

            if item_specs is None:
                yield element.get_text()
                continue

            item = {}

            for k, s in item_specs.items():
                sel = s.get('sel')

                if sel is not None:
                    sub_element = element.select(sel)[0]
                else:
                    sub_element = element

                # Empty value
                v = None

                # Extraction methods
                if s.get('method') == 'text':
                    v = sub_element.get_text()

                # Attributes
                else:
                    attr = s.get('attr')

                    if attr is not None:
                        v = sub_element.get(attr)

                item[k] = v

            yield item


def scrape(html, specs):
    soup = BeautifulSoup(html, 'lxml')

    return scrape_from_soup(soup, specs)


