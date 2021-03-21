# =============================================================================
# Minet Scrape Unit Tests
# =============================================================================
from bs4 import BeautifulSoup
from minet.scrape import scrape, headers_from_definition, tabulate

BASIC_HTML = """
    <ul>
        <li id="li1">One</li>
        <li id="li2">Two</li>
    </ul>
"""

HOLEY_HTML = """
    <ul>
        <li id="li1">One</li>
        <li>Two</li>
        <li id="li3">Three</li>
    </ul>
"""

REPETITIVE_HTML = """
    <ul>
        <li id="li1">One</li>
        <li id="li1">Two</li>
        <li id="li3">Three</li>
    </ul>
"""


NESTED_HTML = """
    <ul>
        <li id="li1" class="li"><span class="first">One</span> <span class="second">1</span></li>
        <li id="li2" class="li"><span class="first">Two</span> <span class="second">2</span></li>
    </ul>
"""

META_HTML = """
    Exemple
    <div id="ok">
        <ul>
            <li id="li1">One</li>
            <li id="li2">Two</li>
        </ul>
    </div>
"""

TABLE_TH_HTML = """
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Surname</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>John</td>
                <td>Mayall</td>
            </tr>
            <tr>
                <td>Mary</td>
                <td>Susan</td>
            </tr>
        </tbody>
    </table>
"""


class TestScrape(object):
    def test_basics(self):
        result = scrape({
            'iterator': 'li'
        }, BASIC_HTML)

        assert result == ['One', 'Two']

        result = scrape({
            'iterator': 'li',
            'item': 'id'
        }, BASIC_HTML)

        assert result == ['li1', 'li2']

        result = scrape({
            'iterator': 'li',
            'item': {
                'attr': 'id'
            }
        }, BASIC_HTML)

        assert result == ['li1', 'li2']

        result = scrape({
            'sel': '#ok',
            'item': 'id'
        }, META_HTML)

        assert result == 'ok'

        result = scrape({
            'sel': '#ok',
            'iterator': 'li',
            'item': 'id'
        }, META_HTML)

        assert result == ['li1', 'li2']

        result = scrape({
            'iterator': 'li',
            'item': {
                'eval': 'element.get("id") + "-ok"'
            }
        }, BASIC_HTML)

        assert result == ['li1-ok', 'li2-ok']

        result = scrape({
            'iterator': 'li',
            'item': {
                'attr': 'id',
                'eval': 'value + "-test"'
            }
        }, BASIC_HTML)

        result == ['li1-test', 'li2-test']

        result = scrape({
            'iterator': 'li',
            'fields': {
                'id': 'id',
                'text': 'text'
            }
        }, BASIC_HTML)

        assert result == [{'id': 'li1', 'text': 'One'}, {'id': 'li2', 'text': 'Two'}]

        result = scrape({
            'iterator': 'li',
            'fields': {
                'label': {
                    'sel': '.first'
                },
                'number': {
                    'sel': '.second'
                }
            }
        }, NESTED_HTML)

        assert result == [{'number': '1', 'label': 'One'}, {'number': '2', 'label': 'Two'}]

        result = scrape({
            'iterator': 'li',
            'fields': {
                'inner': {
                    'extract': 'inner_html'
                },
                'outer': {
                    'extract': 'outer_html'
                }
            }
        }, NESTED_HTML)

        assert result == [
            {
                'inner': '<span class="first">One</span> <span class="second">1</span>',
                'outer': '<li class="li" id="li1"><span class="first">One</span> <span class="second">1</span></li>'
            },
            {
                'inner': '<span class="first">Two</span> <span class="second">2</span>',
                'outer': '<li class="li" id="li2"><span class="first">Two</span> <span class="second">2</span></li>'
            }
        ]

        result = scrape({
            'it': 'li',
            'fields': {
                'value': 'text',
                'constant': {
                    'default': 'Same'
                }
            }
        }, BASIC_HTML)

        assert result == [{'value': 'One', 'constant': 'Same'}, {'value': 'Two', 'constant': 'Same'}]

        result = scrape({
            'iterator': 'li',
            'item': {
                'attr': 'class',
                'default': 'no-class'
            }
        }, BASIC_HTML)

        assert result == ['no-class', 'no-class']

        result = scrape({
            'iterator': 'li',
            'item': {
                'attr': 'id',
                'format': 'id = {value}'
            }
        }, BASIC_HTML)

        assert result == ['id = li1', 'id = li2']

    def test_filter(self):
        result = scrape({
            'iterator': 'li',
            'item': 'id'
        }, HOLEY_HTML)

        assert result == ['li1', None, 'li3']

        result = scrape({
            'iterator': 'li',
            'item': 'id',
            'filter_eval': 'bool(value)'
        }, HOLEY_HTML)

        assert result == ['li1', 'li3']

        result = scrape({
            'iterator': 'li',
            'item': 'id',
            'filter': True
        }, HOLEY_HTML)

        assert result == ['li1', 'li3']

        result = scrape({
            '$$': 'li',
            'fields': {
                'id': 'id'
            },
            'filter': True
        }, HOLEY_HTML)

        assert result == [{'id': 'li1'}, {'id': None}, {'id': 'li3'}]

        result = scrape({
            'iterator': 'li',
            'fields': {
                'id': 'id'
            },
            'filter': 'id'
        }, HOLEY_HTML)

        assert result == [{'id': 'li1'}, {'id': 'li3'}]

    def test_uniq(self):
        result = scrape({
            'iterator': 'li',
            'item': 'id',
            'uniq': True
        }, REPETITIVE_HTML)

        assert result == ['li1', 'li3']

        result = scrape({
            'iterator': 'li',
            'fields': {
                'id': 'id'
            },
            'uniq': 'id'
        }, REPETITIVE_HTML)

        assert result == [{'id': 'li1'}, {'id': 'li3'}]

    def test_recursive(self):
        result = scrape({
            'iterator': 'li',
            'item': {
                'iterator': 'span'
            }
        }, NESTED_HTML)

        assert result == [['One', '1'], ['Two', '2']]

    def test_selection_eval(self):

        result = scrape({
            'iterator': 'li',
            'item': {
                'sel_eval': 'element.select_one("span")'
            }
        }, NESTED_HTML)

        assert result == ['One', 'Two']

        result = scrape({
            'iterator_eval': 'element.select("li") + element.select("span")',
            'item': {
                'attr': 'class'
            }
        }, NESTED_HTML)

        assert result == [['li'], ['li'], ['first'], ['second'], ['first'], ['second']]

    def test_eval(self):
        result = scrape({
            'iterator': 'li',
            'fields': {
                'root_id': {
                    'eval': 'root.select_one("#ok").get("id")'
                }
            }
        }, META_HTML)

        assert result == [{'root_id': 'ok'}, {'root_id': 'ok'}]

        result = scrape({
            'item': {
                'eval': 'html.split("<div", 1)[0].strip()'
            }
        }, META_HTML)

        assert result == 'Exemple'

    def test_context(self):
        result = scrape({
            'iterator': 'li',
            'fields': {
                'text': {
                    'method': 'text'
                },
                'context': {
                    'eval': 'context["value"]'
                }
            }
        }, BASIC_HTML, context={'value': 1})

        assert list(result) == [
            {'text': 'One', 'context': 1},
            {'text': 'Two', 'context': 1}
        ]

        result = scrape({
            'iterator': 'li',
            'fields': {
                'text': {
                    'method': 'text'
                },
                'context': {
                    'get': 'value'
                }
            }
        }, BASIC_HTML, context={'value': 1})

        assert list(result) == [
            {'text': 'One', 'context': 1},
            {'text': 'Two', 'context': 1}
        ]

        result = scrape({
            'context': {
                'divid': {
                    '$': '#ok',
                    'attr': 'id'
                }
            },
            'iterator': 'li',
            'fields': {
                'context': {
                    'get': 'divid'
                },
                'value': 'text'
            }
        }, META_HTML)

        assert result == [{'context': 'ok', 'value': 'One'}, {'context': 'ok', 'value': 'Two'}]

        result = scrape({
            'context': {
                'title': {
                    'default': 'Scrape'
                }
            },
            'iterator': 'li',
            'fields': {
                'local': {
                    'context': {
                        'divid': {
                            'eval': 'root.select_one("#ok").get("id")'
                        }
                    },
                    'get': 'divid'
                },
                'global': {
                    'get': 'divid'
                },
                'title': {
                    'get': 'title'
                }
            }
        }, META_HTML, context={'divid': 'notok'})

        assert result == [
            {'local': 'ok', 'global': 'notok', 'title': 'Scrape'},
            {'local': 'ok', 'global': 'notok', 'title': 'Scrape'}
        ]

    def test_tabulate(self):
        soup = BeautifulSoup(TABLE_TH_HTML, 'lxml')
        table = soup.select_one('table')

        result = list(tabulate(table))

        assert result == [{'Name': 'John', 'Surname': 'Mayall'}, {'Name': 'Mary', 'Surname': 'Susan'}]

        result = list(tabulate(table, headers=['name', 'surname']))

        assert result == [{'name': 'John', 'surname': 'Mayall'}, {'name': 'Mary', 'surname': 'Susan'}]

    def test_headers(self):
        headers = headers_from_definition({'iterator': 'li'})

        assert headers == ['value']

        headers = headers_from_definition({'iterator': 'li', 'item': 'id'})

        assert headers == ['value']

        headers = headers_from_definition({'iterator': 'li', 'fields': {'id': 'id'}})

        assert headers == ['id']

        headers = headers_from_definition({'sel': 'table', 'tabulate': {'headers': ['id']}})

        assert headers == ['id']

        headers = headers_from_definition({'sel': 'table', 'tabulate': True})

    def test_absent_tail_call(self):
        item = scrape({
            'sel': 'quote',
            'fields': {
                'url': 'href'
            }
        }, BASIC_HTML)

        assert item is None

    def test_inexistent_selection(self):
        expected = [{'id': 'li1', 'empty': None}, {'id': 'li2', 'empty': None}]

        items = scrape({
            'it': 'li',
            'fields': {
                'id': 'id',
                'empty': {
                    'sel': 'blockquote'
                }
            }
        }, BASIC_HTML)

        assert items == expected

        items = scrape({
            'it': 'li',
            'fields': {
                'id': 'id',
                'empty': {
                    'sel': 'blockquote',
                    'item': 'text'
                }
            }
        }, BASIC_HTML)

        assert items == expected

        item = scrape({
            'sel': 'li',
            'fields': {
                'id': 'id',
                'empty': {
                    'sel': 'blockquote',
                    'item': 'text'
                }
            }
        }, BASIC_HTML)

        assert item == expected[0]
