# Minet Scraping DSL Tutorial

[Scraping](https://en.wikipedia.org/wiki/Web_scraping) is a web mining task that is usually done using some kind of script language such as `python`. However, since `minet` is first and foremost a CLI tool, we need to find another way to declare our scraping intentions.

So, in order to facilitate scraping, `minet` uses a custom declarative [DSL](https://en.wikipedia.org/wiki/Domain-specific_language), typically written in [JSON](https://en.wikipedia.org/wiki/JSON) or [YAML](https://en.wikipedia.org/wiki/YAML).

Here is therefore a full tutorial about the capabilities of this DSL.

Note that all examples will be presented in YAML format, but any JSON-like format will also do the trick just find. It's just that YAML is kind of the python of JSON and is somewhat quicker to write, which is always a nice thing to have, at least in this context. Also, YAML has comments and it makes it easier to explain what's happening in this tutorial.

## Summary

## Scraping a single item

Let's start easy, we only need to scrape a single thing from our HTML page: its title. The title is usually the text contained in the `<title>` tag:

```html
<html>
  <head>
    <title>
      My Awesome Web Page
    </title>
  </head>
  <body>
    ...
  </body>
</html>
```

So, here is the simplest scraper ever:

```yml
---
sel: title # Here we use CSS selection to target the first <title> tag
```

Applying this scraper on the beforementioned HTML will yield the following result:

```
My Awesome Web Page
```

Two things should be noted here:

1. In the absence of any additional information, the scraper will fallback to extract the nodes' text.
2. Extracted text is always stripped (or trimmed, if you come from another language than python) of its leading and trailing whitespace for convenience.


## Aliases
