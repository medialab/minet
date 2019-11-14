# Minet Scraping DSL Tutorial

[Scraping](https://en.wikipedia.org/wiki/Web_scraping) is a web mining task that is usually done using some kind of script language such as `python`. However, since `minet` is first and foremost a CLI tool, we need to find another way to declare our scraping intentions.

So, in order to facilitate scraping, `minet` uses a custom declarative [DSL](https://en.wikipedia.org/wiki/Domain-specific_language) (**D**omain **S**pecific **L**anguage), typically written in [JSON](https://en.wikipedia.org/wiki/JSON) or [YAML](https://en.wikipedia.org/wiki/YAML).

Here is therefore a full tutorial about the capabilities of this DSL.

Note that all examples will be presented in YAML format, even if any JSON-like format would also do the trick just fine. It's just that YAML is kind of the python of JSON and is somewhat quicker to write, which is always a nice in this context. Also, YAML has comments and it makes it easier to explain what's happening throughout the tutorial.

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
    <div id="main" title="hello">Hello World!</div>
  </body>
</html>
```

So, here is the simplest scraper ever:

```yml
---
sel: title # Here we use CSS selection to target the first <title> tag
```

If you are a bit shaky about CSS selection and want to refresh your memory or simply learn, I can't recommand you [this](https://flukeout.github.io/) wonderful tutorial enough.

Applying this scraper on the beforementioned HTML will yield the following result:

```json
"My Awesome Web Page"
```

Two things should be noted here:

1. In the absence of any additional information, the scraper will fallback to extract the node's text.
2. Extracted text is always stripped of its leading and trailing whitespace for convenience.

## Declaring what to extract

But maybe we want something more than a selected node's text. What if we want its inner html? Or one of its attribute? Then we need to say so using the `item` key:

```yml
---
sel: body
item: html # Here, we want the node's inner html
```

This will yield:

```json
"<div id=\"main\" class=\"container\">Hello World!</div>"
```

Note that the first example we saw is actually a shorthand for:

```yml
---
sel: title
item: text
```

But what if we want to extract a node's attribute? Well it's as simple as:

```yml
---
# Note that here I wrap the selector in quotes so that YAML
# does not interpret this as a comment
sel: '#main'
item: title
```

This will naturally yield:

```json
"hello"
```

So, to recap, here is what `item` can be:

1. `text` to extract the selected node's text (this is the same as not declaring `item`)
2. `html` or `inner_html` to extract the selected node's inner html
3. `outer_html` to extract the selected node's outer html
4. the name of any of the selected node's attributes

## Declaring multiple fields to extract

Now we might want to extract several pieces of informations from our selected node rather than a single one. To do so, we can use the `field` key, **instead** of `item` to structure the output:

```yml
---
sel: '#main'
fields:
  content: text
  title: title
```

This will yield:

```json
{
  "content": "Hello World!",
  "title": "hello"
}
```

## Iterating over multiple nodes

So far, we now how to select a single node and extract information about it. But oftentimes, we want to iterate over a selection of nodes and extract information about each of them.

Let's consider the following page:

```html
<main>
  <article>
    <h2>
      <a href="http://howtoscrape.com">
        How to scrape?
      </a>
    </h2>
    <div>
      Posted by <span>George</span>
    </div>
  </article>
  <article>
    <h2>
      <a href="http://howtocrawl.co.uk">
        How to crawl?
      </a>
    </h2>
    <div>
      Posted by <span>Mary</span>
    </div>
  </article>
</main>
```

To be able to iterate over the page's articles, we will use the `iterator` key to be able to select multiple nodes from which to extract information:

```yml
---
iterator: article a # This is still CSS selection
```

This will yield an array containing one item per selected node:

```json
[
  "How to scrape?",
  "How to crawl?"
]
```

You can of course still use the `item` and `fields` keys to declare finely what to extract:

```yml
---
iterator: article a
item: href
```

will yield:

```json
[
  "http://howtoscrape.com",
  "http://howtocrawl.co.uk"
]
```

```yml
iterator: article a
fields:
  title: text
  url: href
```

will yield:

```json
[
  {
    "title": "How to scrape?",
    "url": "http://howtoscrape.com"
  },
  {
    "title": "How to crawl?",
    "url": "http://howtocrawl.co.uk"
  }
]
```

## Subselection

## Aliases

## Recursivity
