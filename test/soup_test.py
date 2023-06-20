import pytest

from minet.scrape.soup import WonderfulSoup, SelectionError

HTML = """
<div>
    <p>wut?</p>
</div>
"""

LINKS = """
    <h1 id="title">Title</h1>
    <ul>
        <li><a href="one">1</a></li>
        <li><a href="two">2</a></li>
    </ul>
"""


class TestWonderfulSoup:
    def test_select_one_strict(self):
        with pytest.raises(SelectionError):
            WonderfulSoup(HTML).select_one("li", strict=True)

    def test_get_display_text(self):
        soup = WonderfulSoup(HTML)

        assert soup.get_display_text() == "wut?"
        assert soup.select_one("p", strict=True).get_display_text() == "wut?"

    def test_get_html(self):
        soup = WonderfulSoup(HTML)

        p = soup.select_one("p", strict=True)

        assert p.get_html() == "wut?"
        assert p.get_inner_html() == "wut?"
        assert p.get_outer_html() == "<p>wut?</p>"

    def test_contains(self):
        soup = WonderfulSoup(HTML)

        assert soup.select_one(':contains("wut")') is not None
        assert soup.select(':contains("wut")') is not None

    def test_scrape_one(self):
        soup = WonderfulSoup(LINKS)

        assert soup.scrape_one("h1") == "Title"
        assert soup.scrape_one("link") is None

        with pytest.raises(SelectionError):
            assert soup.scrape_one("link", strict=True)
