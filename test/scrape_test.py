# =============================================================================
# Minet Scrape Unit Tests
# =============================================================================
from minet.scrape import scrape, headers_from_definition

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

    def test_headers(self):
        headers = headers_from_definition({'iterator': 'li'})

        assert headers == ['value']

        headers = headers_from_definition({'iterator': 'li', 'item': 'id'})

        assert headers == ['value']

        headers = headers_from_definition({'iterator': 'li', 'fields': {'id': 'id'}})

        assert headers == ['id']
