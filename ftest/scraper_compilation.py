from pprint import pprint
from bs4 import BeautifulSoup
from minet import Scraper
from minet.scrape.compiler import compile_scraper
from minet.scrape.analysis import validate, report_validation_errors

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


# def test(definition, target):
#     compiled = compile_scraper(definition, as_string=True)

#     print('Scraper:')
#     print('--------')
#     print()
#     print(compiled)

#     scraper = compile_scraper(definition)

#     soup = BeautifulSoup(target, 'lxml')

#     print('Output:')
#     print('-------')
#     pprint(scraper(soup))
#     print()
#     print()

# test({
#     'iterator': 'ul > li',
#     'item': 'id'
# }, BASIC_HTML)

# test({
#     'iterator': 'div',
#     'item': {
#         'iterator': 'ul',
#         'item': {
#             'iterator': 'li'
#         }
#     }
# }, RECURSIVE_HTML)

# test({
#     'iterator': 'ul > li',
#     'fields': {
#         'id': 'id',
#         'text': 'text'
#     }
# }, BASIC_HTML)

# test({
#     'iterator': 'div',
#     'item': {
#         'iterator': 'ul',
#         'fields': {
#             'id': 'id',
#             'items': {
#                 'iterator': 'li',
#                 'fields': {
#                     'text': 'text',
#                     'color': 'color'
#                 }
#             }
#         }
#     }
# }, RECURSIVE_HTML)

# test({
#     'iterator': 'div',
#     'fields': {
#         'align': 'align',
#         'items': {
#             'iterator': 'ul',
#             'fields': {
#                 'id': 'id',
#                 'items': {
#                     'iterator': 'li',
#                     'fields': {
#                         'text': 'text',
#                         'color': 'color'
#                     }
#                 }
#             }
#         }
#     }
# }, RECURSIVE_HTML)

# from timeit import default_timer as timer

# class Timer(object):
#     def __init__(self, name='Timer'):
#         self.name = name

#     def __enter__(self):
#         self.start = timer()

#     def __exit__(self, *args):
#         self.end = timer()
#         self.duration = self.end - self.start
#         print('%s:' % self.name, self.duration)

# RECURSIVE_SCRAPER_DEFINITION = {
#     'iterator': 'div',
#     'fields': {
#         'align': 'align',
#         'items': {
#             'iterator': 'ul',
#             'fields': {
#                 'id': 'id',
#                 'items': {
#                     'iterator': 'li',
#                     'fields': {
#                         'text': 'text',
#                         'color': 'color'
#                     }
#                 }
#             }
#         }
#     }
# }

# N = 10_000

# with Timer('runtime'):
#     scraper = Scraper(RECURSIVE_SCRAPER_DEFINITION)
#     soup = BeautifulSoup(RECURSIVE_HTML, 'lxml')

#     for _ in range(N):
#         scraper(soup)

# with Timer('compilation'):
#     scraper = compile_scraper(RECURSIVE_SCRAPER_DEFINITION)
#     soup = BeautifulSoup(RECURSIVE_HTML, 'lxml')

#     for _ in range(N):
#         scraper(soup)

THE_WORST_SCRAPER_EVER = {
    'sel': 'li',
    'item': {
        'sel': 'a[',
        'eval': '"ok'
    },
    'filter': True,
    'fields': {
        'url': {
            'iterator': ':first',
            'iterator_eval': '"span"'
        },
        'name': {
            'attr': 'id',
            'extract': 'text'
        },
        'id': {
            'attr': 'id',
            'item': 'href'
        },
        'code': {
            'eval': 'a = 45\nif a == 34:\n  return a\nif'
        }
    }
}

errors = validate(THE_WORST_SCRAPER_EVER)

# for error in errors:
#     print(repr(error))

report = report_validation_errors(errors)

print()
print(report)
