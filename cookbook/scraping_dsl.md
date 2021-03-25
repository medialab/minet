# Minet Scraping DSL Tutorial

[Scraping](https://en.wikipedia.org/wiki/Web_scraping) is a web mining task that is usually done using some kind of script language such as `python`. However, since `minet` is first and foremost a CLI tool, we need to find another way to declare our scraping intentions.

So, in order to enable efficient scraping, `minet` uses a custom declarative [DSL](https://en.wikipedia.org/wiki/Domain-specific_language) (**D**omain **S**pecific **L**anguage), typically written in [JSON](https://en.wikipedia.org/wiki/JSON) or [YAML](https://en.wikipedia.org/wiki/YAML) and reminiscent of [artoo.js](https://medialab.github.io/artoo/), a JavaScript webmining tool, scraping utilities.

Here is therefore a full tutorial about the capabilities of this DSL.

Note that all examples will be presented in YAML format, even if any JSON-like format would also do the trick just fine. But YAML being somewhat the python of JSON, is somewhat quicker to write, which is always a nice in this context. Also, YAML has comments and it makes it easier to explain what's happening throughout the tutorial.

Also, if you ever need to read some real examples of scrapers written using the DSL you can check out [this](/ftest/scrapers) folder of the repository.

Finally, this tutorial is fairly long and I encourage you to bail out as soon as you deem you know enough to fit your use-case.

## Summary

* [Applying a minet scraper](#applying-a-minet-scraper)
  * [From python](#from-python)
  * [From the command line](#from-the-command-line)
* [Scraping a single item](#scraping-a-single-item)
* [Declaring what to extract](#declaring-what-to-extract)
* [Declaring multiple fields to extract](#declaring-multiple-fields-to-extract)
* [Iterating over multiple nodes](#iterating-over-multiple-nodes)
* [Subselection](#subselection)
* [Item-level subselection](#item-level-subselection)
* [Nesting data](#nesting-data)
* [Default values](#default-values)
* [Filtering](#filtering)
* [Keeping only unique items](#keeping-only-unique-items)
* [Using evaluation when declarative is not enough](#using-evaluation-when-declarative-is-not-enough)
  * [Evaluating selections](#evaluating-selections)
  * [Evaluating extractions](#evaluating-extractions)
  * [Evaluating filters](#evaluating-filters)
* [Accessing global context](#accessing-global-context)
* [Defining local context](#defining-local-context)
* [Aliases](#aliases)

## Applying a minet scraper

Before learning how to write a `minet` scraper on your own, here is what a scraper extracting a page's `<title>` tag content would look like in YAML format:

```yaml
---
sel: title
```

But how would one actually use it?

### From python

From python you will need to use the `minet.Scraper` class to build your scraper utility like so:

```python
from minet import Scraper

# Creating a scraper from a json declaration file:
scraper = Scraper('scraper.yml')

# Creating a scraper directly from a declaration variable:
declaration = {'sel': 'title'}
scraper = Scraper(declaration)

# You can now apply your scraper on arbitrary html thusly:
title = scraper(html)
```

### From the command line

To use a scraper from the command line, you can use the `scrape` command thusly:

```bash
# To scrape html files recorded in a minet fetch report:
minet scrape scraper.yml report.csv > scraped.csv

# To scrape html file found by glob:
minet scrape scraper.yml --glob 'files/**/*.html' > scraped.csv
```

## Scraping a single item

Let's start easy and let's imagine we only need to scrape a single thing from our HTML page: its title. The title is usually the text contained in the `<title>` tag:

```html
<html>
  <head>
    <title>
      My Awesome Web Page
    </title>
  </head>
  <body>
    <div id="main" data-message="hello">Hello World!</div>
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

1. In the absence of any additional information, the scraper will always fallback to extract the node's text if not instructed otherwise.
2. Extracted text is always stripped of its leading and trailing whitespace for convenience.

## Declaring what to extract

But maybe we want something different than a selected node's text. What if we want its inner html? Or one of its attribute? Then we need to say so using the `item` key:

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
item: data-message
```

This will naturally yield:

```json
"hello"
```

So, to recap, here is what `item` can be:

1. `text` to extract the selected node's text (this is the same as not declaring an `item`)
2. `html` or `inner_html` to extract the selected node's inner html
3. `outer_html` to extract the selected node's outer html
4. the name of any of the selected node's attributes

## Declaring multiple fields to extract

Now we might want to extract several pieces of informations from our selected node rather than a single one. To do so, we can use the `field` key, **instead** of `item` to structure the output:

```yml
---
sel: '#main'
fields: # Here we declare a dictionary of fields to output
  content: text # Each key is now its own `item`
  message: data-message
```

This will yield:

```json
{
  "content": "Hello World!",
  "message": "hello"
}
```

## Iterating over multiple nodes

So far, we now how to select a single node and extract information about it. But oftentimes, we want to iterate over a selection of nodes and extract information about each of them.

Let's consider the following html:

```html
<main>
  <article>
    <h2>
      <a href="http://howtoscrape.com">
        How to scrape?
      </a>
    </h2>
    <div>
      Posted by <strong>George</strong>
    </div>
  </article>
  <article>
    <h2>
      <a href="http://howtocrawl.co.uk">
        How to crawl?
      </a>
    </h2>
    <div>
      Posted by <strong>Mary</strong>
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

Sometimes, it might be useful to be able to perform subselections. For instance, if we consider the following html:

```html
<ul id="fruits">
  <li color="red">Apple</li>
  <li color="orange">Orange</li>
</ul>
<ul id="days">
  <li>Monday</li>
  <li>Saturday</li>
</ul>
```

and if we want to scrape only the fruits, we could write it thusly:

```yml
---
iterator: '#fruits li'
```

or

```yml
sel: '#fruits'
iterator: li
```

and both would yield the same:

```json
[
  "Apple",
  "Orange"
]
```

This basically means than `sel` is applied before the `iterator` selection and this can be useful if you want to separate concerns.

## Item-level subselection

Now it might also be useful to define subselections at `item` or `fields` level. But before being able to do so, we need to understand that `item` can also be defined as an object rather than a simple string for when things need to be more complex:

```yml
---
iterator: '#fruits li'
item:
  extract: text # this is the same as `item: text` or no `item`
```

```yml
---
iterator: '#fruits li'
item:
  attr: color # this is the same as `item: color` but with less ambiguity
```

So now we've learn the following sub keys:

* `extract` can be `text`, `html`, `inner_html` and `outer_html` and does what you expect
* `attr` returns the designated attribute (this means you can also use it if you have the disfortune of needing to extract an attribute named `title` or `html`, for instance).

This of course also works with `fields`:

```yml
iterator: '#fruits li'
fields:
  name:
    extract: text
  color:
    attr: color
```

But now that we have a more expressive way to declare what we want to extract, we can also spice things up with item-level subselections.

Remember this html:

```html
<main>
  <article>
    <h2>
      <a href="http://howtoscrape.com">
        How to scrape?
      </a>
    </h2>
    <div>
      Posted by <strong>George</strong>
    </div>
  </article>
  <article>
    <h2>
      <a href="http://howtocrawl.co.uk">
        How to crawl?
      </a>
    </h2>
    <div>
      Posted by <strong>Mary</strong>
    </div>
  </article>
</main>
```

What if we want to extract both the article's url and the user which posted it?

We can do so by using `sel` in a field declaration:

```yml
---
iterator: main > article
fields:
  url:
    sel: a
    attr: href
  user:
    sel: div > span
```

And this will yield:

```json
[
  {
    "url": "http://howtoscrape.com",
    "user": "George"
  },
  {
    "url": "http://howtocrawl.co.uk",
    "user": "Mary"
  }
]
```

## Nesting data

The next thing to understand is that this scraping DSL is completely recursive. Which should let you describe any kind of JSON-like structure to output.

Let's check this html  again for instance:

```html
<main>
  <ul id="fruits">
    <li color="red">Apple</li>
    <li color="orange">Orange</li>
  </ul>
  <ul id="days">
    <li>Monday</li>
    <li>Saturday</li>
  </ul>
</main>
```

What if we want to return a list of lists of items? Well, say no more:

```yml
---
iterator: main > ul
item:
  iterator: li
```

Harnessing recursivity will return a nested result:

```json
[
  [
    "Apple",
    "Orange"
  ],
  [
    "Monday",
    "Saturday"
  ]
]
```

## Default values

Usually, a scraper will return `None` if a selection cannot be found or if the desired attribute does not exists. If so, you might want to return a default value instead. If we consider the following html for instance:

```html
<ul>
  <li color="blue">John</li>
  <li>Mary</li>
</ul>
```

You could declare a default value thusly:

```yml
---
iterator: li
item:
  attr: color
  default: black
```

And this would return:

```python
["blue", "black"]
```

instead of:

```python
["blue", None]
```

This `default` key can also be thought as a constant value if you ever need one (this could be useful with `minet` crawlers for instance, of if you use several scrapers to track from which one a result came from):

```yml
iterator: li
fields:
  scraper:
    default: 'My scraper'
  name: text
```

would return:

```json
[
  {"scraper": "My Scraper", "name": "John"},
  {"scraper": "My Scraper", "name": "Mary"}
]
```

## Filtering

When iterating on a selection, it might be useful to filter out some empty or invalid results. If we consider the following html:

```html
<ul>
  <li color="blue">John</li>
  <li>Mary</li>
  <li color="purple">Susan</li>
</ul>
```

We can filter out empty values for the `color` attribute using the `filter` key in our scraper:

```yml
---
iterator: li
item: color
filter: yes # yes is just one of the multiple ways to say `true` in YAML
```

This should return:

```json
["blue", "purple"]
```

and not:

```python
["blue", None, "purple"]
```

Note that this `filter` key can also take a path to the value to actually test for filtering when using, for instance, `fields` like so:

```yml
---
iterator: li
fields:
  name: text
  color: color
filter: color
```

will return:

```json
[
  {"name": "John", "color": "blue"},
  {"name": "Susan", "color": "purple"}
]
```

Note that the path given to `filter` can be an array or keys separated by a point if you need to test nested values.

Finally, if you need more complex filtering, you can still read about `filter_eval` [here](#evaluating-filters).

## Keeping only unique items

When iterating on a selection to return multiple items, you might get the same one multiple times and you might want to avoid that.

If we, for instance, consider the following html:

```html
<ul>
  <li color="blue">John</li>
  <li color="red">Mary</li>
  <li color="blue">Susan</li>
</ul>
```

You can use the `uniq` key to be sure scraping the `color` attributes will only yield `"blue"` once:

```yml
---
iterator: li
item: color
uniq: yes
```

and you will get:

```json
["blue", "red"]
```

instead of:

```json
["blue", "red", "blue"]
```

If you only want to keep a single item based on one of its fields, you can give a path to the `uniq` key, the same way you would with `filter`. Just note that the item that will be kept is the first occurring one having a given value at the given path so that the following scraper:

```yml
iterator: li
fields:
  name: text
  color: color
uniq: color
```

will return:

```json
[
  {"name": "John", "color": "blue"},
  {"name": "Mary", "color": "red"}
]
```

## Using evaluation when declarative is not enough

### Evaluating selections

### Evaluating extractions

### Evaluating filters

## Accessing global context

## Defining local context

## Aliases

Know that some of the DSL keys have aliases for convenience:

* `sel` can also be written as `$` (which is reminiscent of web development)
* `iterator` can also be written as `$$`

So don't be surprised if you see them appear in people code's sometimes and don't be afraid to use them if they fit your mindset better.
