from bs4 import BeautifulSoup
from minet import Scraper
from minet.scrape.compilation import compile_scraper

BASIC_HTML = """
    <ul>
        <li id="li1">One</li>
        <li id="li2">Two</li>
    </ul>
"""

RECURSIVE_HTML = """
    <main>
        <div>
            <ul id="fruits">
                <li color="red">Apple</li>
                <li color="orange">Orange</li>
            </ul>
            <ul id="days">
                <li>Monday</li>
                <li>Saturday</li>
            </ul>
        </div>
        <div>
            <ul id="names">
                <li>John</li>
                <li>Mary</li>
            </ul>
            <ul id="animals">
                <li>Dog</li>
                <li>Cat</li>
            </ul>
        </div>
    </main>
"""


def test(definition, target):
    compiled = compile_scraper(definition, as_string=True)

    print('Scraper:')
    print('--------')
    print()
    print(compiled)

    scraper = compile_scraper(definition)

    soup = BeautifulSoup(target, 'lxml')

    print()
    print('Output:')
    print('-------')
    print(scraper(soup))
    print()

test({
    'iterator': 'ul > li',
    'item': 'id'
}, BASIC_HTML)

test({
    'iterator': 'div',
    'item': {
        'iterator': 'ul',
        'item': {
            'iterator': 'li'
        }
    }
}, RECURSIVE_HTML)
