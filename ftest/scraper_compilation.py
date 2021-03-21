from pprint import pprint
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
        <div align="left">
            <ul id="fruits">
                <li color="red">Apple</li>
                <li color="orange">Orange</li>
            </ul>
            <ul id="days">
                <li color="yellow">Monday</li>
                <li color="blue">Saturday</li>
            </ul>
        </div>
        <div align="right">
            <ul id="names">
                <li color="brown">John</li>
                <li color="cyan">Mary</li>
            </ul>
            <ul id="animals">
                <li color="gray">Dog</li>
                <li color="black">Cat</li>
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

    print('Output:')
    print('-------')
    pprint(scraper(soup))
    print()
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

test({
    'iterator': 'ul > li',
    'fields': {
        'id': 'id',
        'text': 'text'
    }
}, BASIC_HTML)

test({
    'iterator': 'div',
    'item': {
        'iterator': 'ul',
        'fields': {
            'id': 'id',
            'items': {
                'iterator': 'li',
                'fields': {
                    'text': 'text',
                    'color': 'color'
                }
            }
        }
    }
}, RECURSIVE_HTML)

test({
    'iterator': 'div',
    'fields': {
        'align': 'align',
        'items': {
            'iterator': 'ul',
            'fields': {
                'id': 'id',
                'items': {
                    'iterator': 'li',
                    'fields': {
                        'text': 'text',
                        'color': 'color'
                    }
                }
            }
        }
    }
}, RECURSIVE_HTML)
