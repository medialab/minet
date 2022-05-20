from bs4 import BeautifulSoup, SoupStrainer

html = '<p id="ok">test</p><span>whatever</span>'


def strain(tag, attrs):
    print(tag, attrs)


strainer = SoupStrainer(strain)

soup = BeautifulSoup(html, "lxml", parse_only=strainer)
