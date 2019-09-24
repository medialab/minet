# =============================================================================
# Minet Scrape Function
# =============================================================================
#
# Function interpreting minet's scraping JSON descriptive DSL format to
# actually scrape content off of HTML content.
#
import re
from bs4 import BeautifulSoup


def extract_value(element, spec, root=None, html=None, context=None):

    # No specs -> returning text
    if spec is None:
        return element.get_text()

    # If spec is a string, we want an attribute
    if isinstance(spec, str):
        return element.get(spec)

    # Dictionary?
    fields = spec.get('fields')

    if fields is not None:
        o = {}

        for k, s in fields.items():
            v = extract_value(element, s, root, html, context)

            if v is not None:
                o[k] = v

        return o

    # Subselection
    sel = spec.get('sel')
    elements = [element]

    if sel is not None:
        elements = element.select(sel)

        if not elements:
            return spec.get('default')

        element = elements[0]

    value = element.get_text()

    # Retrieving attributes
    attr = spec.get('attr')

    if attr is not None:
        value = element.get(attr)

    # Retrieving raw text or html etc.
    # TODO...

    # Eval?
    expression = spec.get('eval')

    if expression is not None:
        return eval(expression, None, {

            # Useful deps
            're': re,

            # Local values
            'element': element,
            'elements': elements,
            'value': value,

            # Context
            'html': html,
            'root': root
        })

    return value


def scrape_from_soup(soup, specs, html=None):
    item_specs = specs.get('item')

    iterator = specs.get('iterator')

    if iterator is None:
        elements = [soup]
    else:
        elements = soup.select(iterator)

    for element in elements:
        yield extract_value(
            element,
            item_specs,
            root=soup,
            html=html
        )


def scrape(html, specs):
    soup = BeautifulSoup(html, 'lxml')

    return scrape_from_soup(soup, specs, html)


def headers_from_definition(specs):
    item = specs.get('item')
    fields = item.get('fields') if isinstance(item, dict) else None

    if fields is None or isinstance(item, str):
        return ['value']

    return list(item['fields'].keys())
