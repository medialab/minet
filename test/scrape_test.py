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

class TestScrape(object):
    def test_basics(self):
        result = scrape(BASIC_HTML, {
            'iterator': 'li'
        })

        assert list(result) == ['One', 'Two']

        result = scrape(BASIC_HTML, {
            'iterator': 'li',
            'item': {
                'id': {
                    'attr': 'id'
                },
                'text': {
                    'method': 'text'
                }
            }
        })

        assert list(result) == [{'id': 'li1', 'text': 'One'}, {'id': 'li2', 'text': 'Two'}]
