from minet.scrape.soup import WonderfulSoup

HTML = """
<div>
    <p>wut?</p>
</div>
"""


class TestWonderfulSoup:
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
