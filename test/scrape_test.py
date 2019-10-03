# =============================================================================
# Minet Scrape Unit Tests
# =============================================================================
from minet.scrape import scrape

BASIC_HTML = """
    <ul>
        <li id="li1">One</li>
        <li id="li2">Two</li>
    </ul>
"""

NESTED_HTML = """
    <ul>
        <li id="li1"><span class="first">One</span> <span class="second">1</span></li>
        <li id="li2"><span class="first">Two</span> <span class="second">2</span></li>
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


class TestScrape(object):
    def test_basics(self):
        result = scrape({
            'iterator': 'li'
        }, BASIC_HTML)

        assert result == ['One', 'Two']

    #     result = scrape(BASIC_HTML, {
    #         'iterator': 'li',
    #         'item': 'id'
    #     })

    #     assert list(result) == ['li1', 'li2']

    #     result = scrape(BASIC_HTML, {
    #         'iterator': 'li',
    #         'item': {
    #             'eval': 'element.get("id") + "-ok"'
    #         }
    #     })

    #     assert list(result) == ['li1-ok', 'li2-ok']

    #     result = scrape(BASIC_HTML, {
    #         'iterator': 'li',
    #         'item': {
    #             'attr': 'id',
    #             'eval': 'value + "-test"'
    #         }
    #     })

    #     assert list(result) == ['li1-test', 'li2-test']

    #     result = scrape(BASIC_HTML, {
    #         'iterator': 'li',
    #         'item': {
    #             'fields': {
    #                 'id': {
    #                     'attr': 'id'
    #                 },
    #                 'text': {
    #                     'method': 'text'
    #                 }
    #             }
    #         }
    #     })

    #     assert list(result) == [{'id': 'li1', 'text': 'One'}, {'id': 'li2', 'text': 'Two'}]

    #     result = scrape(NESTED_HTML, {
    #         'iterator': 'li',
    #         'item': {
    #             'fields': {
    #                 'label': {
    #                     'sel': '.first'
    #                 },
    #                 'number': {
    #                     'sel': '.second'
    #                 }
    #             }
    #         }
    #     })

    #     assert list(result) == [{'number': '1', 'label': 'One'}, {'number': '2', 'label': 'Two'}]

    def test_recursive(self):
        result = scrape({
            'iterator': 'li',
            'item': {
                'iterator': 'span'
            }
        }, NESTED_HTML)

        assert result == [['One', '1'], ['Two', '2']]

    # def test_context(self):
    #     result = scrape(META_HTML, {
    #         'iterator': 'li',
    #         'item': {
    #             'fields': {
    #                 'root_id': {
    #                     'eval': 'root.select_one("#ok").get("id")'
    #                 }
    #             }
    #         }
    #     })

    #     assert list(result) == [{'root_id': 'ok'}, {'root_id': 'ok'}]

    #     result = scrape(META_HTML, {
    #         'item': {
    #             'eval': 'html.split("<div", 1)[0].strip()'
    #         }
    #     })

    #     assert list(result) == ['Exemple']

    #     result = scrape(BASIC_HTML, {
    #         'iterator': 'li',
    #         'item': {
    #             'fields': {
    #                 'text': {
    #                     'method': 'text'
    #                 },
    #                 'context': {
    #                     'eval': 'context["value"]'
    #                 }
    #             }
    #         }
    #     }, context={'value': 1})

    #     assert list(result) == [
    #         {'text': 'One', 'context': 1},
    #         {'text': 'Two', 'context': 1}
    #     ]

    # def test_headers(self):
    #     headers = headers_from_definition({'iterator': 'li'})

    #     assert headers == ['value']

    #     headers = headers_from_definition({'iterator': 'li', 'item': 'id'})

    #     assert headers == ['value']

    #     headers = headers_from_definition({'iterator': 'li', 'item': {'fields': {'id': 'id'}}})

    #     assert headers == ['id']
