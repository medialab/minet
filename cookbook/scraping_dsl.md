# Minet Scraping DSL Tutorial

[Scraping](https://en.wikipedia.org/wiki/Web_scraping) is a web mining task that is usually done using some kind of script language such as `python`. However, since `minet` is first and foremost a CLI tool, we need to find another way to declare our scraping intentions.

So, in order to facilitate scraping, `minet` uses a custom declarative [DSL](https://en.wikipedia.org/wiki/Domain-specific_language) (**D**omain **S**pecific **L**anguage), typically written in [JSON](https://en.wikipedia.org/wiki/JSON) or [YAML](https://en.wikipedia.org/wiki/YAML).

Here is therefore a full tutorial about the capabilities of this DSL.

Note that all examples will be presented in YAML format, even if any JSON-like format would also do the trick just fine. It's just that YAML is kind of the python of JSON and is somewhat quicker to write, which is always a nice in this context. Also, YAML has comments and it makes it easier to explain what's happening throughout the tutorial.

Also, if you ever need to read some real examples of scrapers written using the DSL you can check out [this](/ftest/scrapers) folder of the repository.

Finally, this tutorial is fairly long and I encourage you to bail out as soon as you deem you know enough to fit your use-case.

## Summary

* [Scraping a single item](#scraping-a-single-item)
* [Declaring what to extract](#declaring-what-to-extract)
* [Declaring multiple fields to extract](#declaring-multiple-fields-to-extract)
* [Iterating over multiple nodes](#iterating-over-multiple-nodes)
* [Subselection](#subselection)
* [Item-level subselection](#item-level-subselection)
* [Recursivity](#recursivity)
* [Constant values](#constant-values)
* [Filtering](#filtering)
* [Keeping only unique items](#keeping-only-unique-items)
* [Formatting values](#formatting-values)
* [Joining results](#joining-results)
* [Tabulating](#tabulating)
* [When declarative is not enough](#when-declarative-is-not-enough)
  * [Evaluating selections](#evaluating-selections)
  * [Evaluating extractions](#evaluating-extractions)
* [Accessing global context](#accessing-global-context)
* [Defining local context](#defining-local-context)
* [Aliases](#aliases)

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
fields: # Here we declare a dictionary of fields to output
  content: text # Each key is now its own `item`
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

Sometimes, it might be useful to be able to perform subselections. For instance, if we consider the following page:

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

Now it might also be useful to define subselections at `item` or `fields` level. But before being able to do so, we need to understand that `item` can also be defined as an object rather than a simple string for when things become complicated:

```yml
---
iterator: '#fruits li'
item:
  extract: text # this is the same as `item: text` or no `item`

---
iterator: '#fruits li'
item:
  attr: color # this is the same as `item: color` but with less ambiguity
```

So now we've learn the following sub keys:

* `extract` can be `text`, `html`, `inner_html` and `outer_html` and does what you expect
* `attr` returns the designated attribute

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

Remember this html page:

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

What if we want to extract both the article's url and the user which posted it?

We can do so by using `sel` in an item declaration:

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

## Recursivity

The next thing to understand is that this scraping DSL is completely recursive. Which should let you describe any kind of JSON-like structure to output.

Let's check this html page again for instance:

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

Harnessing recursivity will return:

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

## Constant values

## Filtering

## Keeping only unique items

## Formatting values

## Joining results

## Tabulating

## When declarative is not enough

### Evaluating selections

### Evaluating extractions

## Accessing global context

## Defining local context

## Aliases

Know that some of the DSL keys have aliases for convenience:

* `sel` can also be written as `$` (which is reminiscent of web development)
* `iterator` can also be written as `it` or `$$`

So don't be surprised if you see them appear in people code's sometimes and don't be afraid to use them if they fit your mindset better.
