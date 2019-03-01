# =============================================================================
# Minet Scrape Unit Tests
# =============================================================================
from minet.scrape import scrape

BASIC_HTML = """
    <ul>
        <li>One</li>
        <li>Two</li>
    </ul>
"""

class TestScrape(object):
    def test_basics(self):
        result = scrape(BASIC_HTML, {
            'iterator': 'li'
        })

        assert list(result) == ['One', 'Two']
