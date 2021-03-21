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

    print('Output:')
    print('-------')
    print(scraper(soup))
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

# def scrape(root, context={}):
#   main_value = None
#   elements_0 = root.select("""ul > li""")
#   value_0 = []
#   for element_0 in elements_0:
#     value_0.append(element_0.get("""id"""))
#   main_value = value_0
#   return main_value

# def scrape_rec(root, context={}):
#   main_value = None
#   elements_0 = root.select("""div""")
#   value_0 = []
#   for element_0 in elements_0:
#     elements_1 = element_0.select("""ul""")
#     value_1 = []
#     for element_1 in elements_1:
#       elements_2 = element_1.select("""li""")
#       value_2 = []
#       for element_2 in elements_2:
#         value_2.append(element_2.get_text().strip())
#       value_1.append(value_2)
#     value_0.append(value_1)
#   main_value = value_0
#   return main_value
