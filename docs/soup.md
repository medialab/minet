# Minet Wonderful Soup

[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) is very fine tool but is ill-adapted to work with modern python [typing](https://docs.python.org/3/library/typing.html).

As such, the `minet.scrape` module provides an enhanced alternative to the `BeautifulSoup` class, shamelessly named `WonderfulSoup`, that is further tailored for typical scraping purposes.

It is also worthy to note that some `minet` utilities, such as the [Response](./web.md#response) class, directly provide wonderful soups instead of beautiful ones (e.g. `response.soup()`).

The interface is mostly identical, except for the parts documented hereafter.

*Example*

```python
from minet.scrape import WonderfulSoup

soup = WonderfulSoup(html)
urls = soup.scrape("a", "href")
```

## A note on CSS selection

`WonderfulSoup` CSS selection was enhanced to natively support the non-standard `:contains()` CSS property (it basically wraps [soupsieve](https://facelessuser.github.io/soupsieve/) `:-soup-contains()` automatically for you).

## A note on extracted text contents

Text content (e.g. what you get with `element.get_text()`) is always automatically stripped of leading and trailing whitespace for you.

## A note on plural attributes

`BeautifulSoup` considers (rightly) some attributes as being plural. This means getting the `class` attribute, for instance, will return a list rather than a single string.

This is useful but can muddy the class usage when relying on python typing. As such, `WonderfulSoup` attribute getters are guaranteed to return singular values only. But you can use the new [`#.get_list`](#get_list) method if you want to keep this convenience locally.

## New methods

- [force_select_one](#force_select_one)
- [get_display_text](#get_display_text)
- [get_html](#get_html)
- [get_inner_html](#get_inner_html)
- [get_outer_html](#get_outer_html)
- [get_list](#get_list)
- [scrape_one](#scrape_one)
- [scrape](#scrape)

### force_select_one

Method "forcing" the selection of the first matching element wrt given CSS selector. That is to say this method will never return `None` if the selector does not match anything but will raise instead. This is often useful when scraping and/or when using python typings.

```python
element = soup.force_select_one("#main_title")
```

### get_display_text

Method returning the "display" text of some element. That is to say the method tries to render the contents of the element by applying browser-like html layout wrt display and inline elements so it can easily be read as raw text.

### get_html

Alias of [#.get_inner_html](#get_inner_html)

### get_inner_html

Method returning the inner html of the element.

### get_outer_html

Method returning the outer html of the element.

### get_list

Return an attribute as a list of whitespace-separated values.

```python
classes = element.get_list("class")
```

### scrape_one

Method scraping text or an attribute value from the first result matching some CSS selector. This method will return `None` if the CSS selector does not match anything. This method will also return `None` if target attribute is not present.

```python
# Scraping text content
text = soup.scrape_one(".content")

# Scraping display text
text = soup.scrape_one(".content", "display_text")

# Scraping some attribute value
url = soup.scrape_one("#next", "href")
```

*Arguments*

- **selector** *str*: CSS selector to match.
- **target** *Optional[str]* `text`: target to extract. Can be one of `text`, `display_text`, `html`, `inner_html`, `outer_html` or the name of an attribute.

### scrape

Method scraping text or an attribute value from all the elements matching some CSS selector. This method will return an empty list if the CSS selector does not match anything. This method will not return empty values for matching elements not having the desired attribute.

```python
# Scraping text content
texts = soup.scrape(".content")

# Scraping display text
texts = soup.scrape(".content", "display_text")

# Scraping some attribute value
urls = soup.scrape(".page-link", "href")
```

*Arguments*

- **selector** *str*: CSS selector to match.
- **target** *Optional[str]* `text`: target to extract. Can be one of `text`, `display_text`, `html`, `inner_html`, `outer_html` or the name of an attribute.
