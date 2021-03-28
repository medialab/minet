# Minet Scraping DSL Tutorial

[Scraping](https://en.wikipedia.org/wiki/Web_scraping) is a web mining task that is usually done using some kind of script language such as `python`. However, since `minet` is first and foremost a CLI tool, we need to find another way to declare our scraping intentions.

So, in order to enable efficient scraping, `minet` uses a custom declarative [DSL](https://en.wikipedia.org/wiki/Domain-specific_language) (**D**omain **S**pecific **L**anguage), typically written in [JSON](https://en.wikipedia.org/wiki/JSON) or [YAML](https://en.wikipedia.org/wiki/YAML) and reminiscent of [artoo.js](https://medialab.github.io/artoo/) scraping [functions](https://medialab.github.io/artoo/scrape/).

The present document is therefore a full tutorial about the capabilities of this DSL.

Also, if you ever need to read some real examples of scrapers written using the DSL you can check out [this](/ftest/scrapers) folder of the repository.

Finally, this tutorial is fairly long so I encourage you to bail out as soon as you deem you know enough to fit your use-case.

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
  * [Evaluating value extraction](#evaluating-value-extraction)
  * [Evaluating filters](#evaluating-filters)
  * [Using functions from within python](#using-functions-from-within-python)
  * [Complete list of exposed variables](#complete-list-of-exposed-variables)
* [Accessing global context](#accessing-global-context)
* [Defining local context](#defining-local-context)
* [Aliases](#aliases)
* [Scraper execution outline](#scraper-execution-outline)
* [Various useful examples](#various-useful-examples)
  * [Going up the tree](#going-up-the-tree)

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

# Creating a scraper from a yaml declaration file:
scraper = Scraper('scraper.yml')

# Creating a scraper directly from a declaration variable:
declaration = {'sel': 'title'}
scraper = Scraper(declaration)

# You can now apply your scraper on arbitrary html thusly:
title = scraper(html)
```

For more information about `minet.Scraper`, be sure to read the relevant documentation [here](../docs/lib.md#scraper).

### From the command line

To use a scraper from the command line, you can use the `scrape` command thusly:

```bash
# To scrape html files recorded in a minet fetch report:
minet scrape scraper.yml report.csv > scraped.csv

# To scrape html file found by using a glob pattern:
minet scrape scraper.yml --glob 'files/**/*.html' > scraped.csv
```

If you want to learn about glob patterns, [this](https://en.wikipedia.org/wiki/Glob_(programming)) wikipedia page can teach you how to build them. In our example `files/**/*.html` basically means we are searching for any file having the `.html` extension in any recursive subfolder found under `files/`.

For more information about the `minet scrape` command, be sure to read the relevant documentation [here](../docs/cli.md#scrape).

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

If you are a bit shaky about CSS selection and want to refresh your memory or simply learn, I can't recommend [this](https://flukeout.github.io/) wonderful tutorial enough.

Note that `minet` uses the popular [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) library to parse and traverse html documents and relies on the [soupsieve](https://facelessuser.github.io/soupsieve/) library for CSS selection.

This said, applying this scraper on the beforementioned HTML will yield the following result:

```json
"My Awesome Web Page"
```

Two things should be noted here:

1. In the absence of any additional information, the scraper will always fallback to extract the node's text if not instructed otherwise.
2. Extracted text is always stripped of its leading and trailing whitespace for convenience.

## Declaring what to extract

But maybe we want something different than a selected node's text. What if we want its inner html? Or one of its attributes? Then we need to say so using the `item` key:

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

Now we might want to extract several pieces of information from our selected node rather than a single one. To do so, we can use the `field` key, **instead** of `item` to structure the output:

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

This `default` key can also be thought as a constant value if you ever need one (this could be useful with `minet` crawlers for instance, or if you use several scrapers to track from which one a result came from):

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
  <li color="blue" age="34">John</li>
  <li age="45">Mary</li>
  <li color="purple" age="23">Susan</li>
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

The `filter` key can also take a field to filter on if `fields` is given, like so:

```yml
---
iterator: li
fields:
  name: text
  color: color
filter: color
```

and this should return:

```json
[
  {"name": "John", "color": "blue"},
  {"name": "Susan", "color": "purple"}
]
```

Note that the path given to `filter` can be also an array or keys joined by a dot to test nested values. Here is such an example:

```yml
---
iterator: li:
fields:
  name: text
  attributes:
    fields:
      color: color
      age: age
filter: attributes.age
```

and you will get:

```json
[
  {"name": "John", "attributes": {"color": "blue", "age": "34"}},
  {"name": "Susan", "attributes": {"color": "purple", "age": "23"}}
]
```

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

If you only want to keep a single item based on one of its `fields`, you can also give a field to the `uniq` key, the same way you would with `filter`.

In this case, only the first item having a given value for the chosen field will be kept so that the following scraper:

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

Sometimes, the DSL will not be enough as you may need to perform complex things with your data that the declaration language does not implement.

In this case, someone with more sense than I would tell you that it is time to start scripting in python directly to cover your use case. But if you still want to benefit from `minet` integration, craft and ecosystem, you can still give scrapers python code as strings to evaluate.

**Warning!**: the `minet` commands have not been designed as anything else than a tool for personal use. As such, as with anything able to execute arbitrary code, you should never trust potential user inputs as safe if you intend to use them as scrapers. This is clearly a security breach! We might add options to toggle off evaluation capabilities of scrapers in the future, but this does not exist as of today.

Now that this is clear, let's learn how to sprinkle some python code on top of our declarative scrapers!

### Evaluating selections

Let's consider the following html:

```html
<main>
  <div id="colors">
    <p>Red</p>
    <p>Blue</p>
  </div>
  <div id="animals">
    <ul>
      <li>Tiger</li>
      <li>Dog</li>
    </ul>
  </div>
</main>
```

If you want to select the items found under each `div` using a condition (yes I know we can get away with some CSS wizardy here, this is a toy example, bear with me please), you will need to evaluate an expression like so:

```yml
---
iterator: div
fields:
  kind: id
  items:
    iterator_eval: "element.select('p') if element.get('id') == 'colors' else element.select('li')"
```

and you will get:

```json
[
  {
    "kind": "colors",
    "items": ["Red", "Blue"]
  },
  {
    "kind": "animals",
    "items": ["Tiger", "Dog"]
  }
]
```

In this example, the local variable `element` is the current html element being iterated on (a `div`, in our case) as represented by [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), a very popular python html representation used by most of scrapers. To get a list of all exposed variables you may use, you can check [this](#complete-list-of-exposed-variables) list.

Note that evaluated strings can either be a single python expression, or more code expressed on multiple lines that should `return` a result at some point. Here is an example of the same logic written on multiple lines in a YAML scraper:

```yml
iterator: div
fields:
  kind: id
  items:
    # Mind the "|" char, it means the followed indented strings will preserve line-returns
    iterator_eval: |
      if element.get('id') == 'color':
        return element.select('p')

      return element.select('li')
```

Of course, the syntax of the evaluated strings will be checked beforehand to check if they are valid python code and any `minet.Scraper` built using bad code will raise validation errors before you can even attempt to use it:

```python
from minet import Scraper
from minet.scrape.exceptions import InvalidScraperError

definition = {
  'iterator': 'div',
  'item': {
    'eval': 'element.get_text() + '
  }
}

try:
  scraper = Scraper(definition)
except InvalidScraperError as e:
  # This error will be raised because "item.eval" is not valid python code!
  # You can check the specific validation error like so:
  for error in e.validation_errors:
    print(repr(error))

  # Note that the command line will report errors for you so you can fix them
```

You should also note that an evaluated expression's results will be typed-checked at runtime to ensure it returned a valid thing. As such `iterator_eval` will yell at you if you make it return something other than a `list` of `bs4.Tag`.

Now, here is another example where we evaluate `sel` instead of `iterator`:

```yml
iterator: div
fields:
  kind: id
  first_item:
    sel_eval: |
      if element.get('id') == 'color':
        return element.select_one('p')

      return element.select_one('li')
```

this will return:

```json
[
  {
    "kind": "colors",
    "first_item": "Red"
  },
  {
    "kind": "animals",
    "first_item": "Tiger"
  }
]
```

Finally, note that both `sel_eval` or `iterator_eval` may also return a single string that will subsquently be used as a CSS selector. As such, this example has the same behavior as the previous one:

```yml
iterator: div
fields:
  kind: id
  first_item:
    sel_eval: |
      if element.get('id') == 'color':
        return 'p'

      return 'li'
```

### Evaluating value extraction

You can also evaluate python code to process and transform the scraped data to make it fit your needs. Let's consider the following html with case variations so ugly it hurts the eyes:

```html
<div id="colors">
  <p>Red</p>
  <p>Blue</p>
  <p>YELLOW</p>
  <p>orange</p>
  <p>ReD</p>
</div>
```

Being a diligent data wrangler, you might want to lowercase all those strings to normalize them. This is where the `eval` key will be able to help you:

```yml
---
iterator: p
item:
  eval: value.lower()
uniq: yes
```

and you will get:

```json
["red", "blue", "yellow", "orange"]
```

In this expression, the `value` variable represents the current value that will be returned and is by default (unless you gave a `default` key) the text of the current html element.

And notice how the `uniq` key applies after your transformation.

Finally, keep in mind that `eval` is the last thing that gets executed. So if you declared an `attr` key, for instance, then the `value` variable will be this attribute's value when the `eval` is run.

To finely understand in which order operations are applied, be sure to read [this](#scraper-execution-outline) part of the tutorial.

### Evaluating filters

The last thing one can "evaluate" is filtering. Let's consider this html:

```html
<ul>
  <li data-status="active">John</li>
  <li data-status="inactive">Mary</li>
  <li data-status="active">Susan</li>
</ul>
```

Now let's imagine you need to filter out `inactive` items. We could do so using the `filter_eval` key (once again, I perfectly know that a finely tuned CSS selector could do the job just fine, but I need an example so let this be a cautionary tale that evaluation is seldom necessary):

```yml
iterator: li
filter_eval: "value != 'inactive'"
```

and, as expected, this will return:

```json
["John", "Mary"]
```

### Using functions from within python

If you build your scraper declaration directly in python, you can replace all the evaluation keys by functions. So, reusing this html from a previous example:

```html
<div id="colors">
  <p>Red</p>
  <p>Blue</p>
  <p>YELLOW</p>
  <p>orange</p>
</div>
```

You could build your scraper thusly:

```python
from minet import Scraper

# the `**kwargs` part is necessary because many arguments will always be given
# so just pick the one you are interested in
def process_value(value, **kwargs):
  return value.upper()

scraper = Scraper({
  'iterator': 'p',
  'item': {
    'eval': process_value
  }
})

scraper(html)
>>> ['RED', 'BLUE', 'YELLOW', 'ORANGE']
```

Keyword arguments given to the function replacing `eval` directives are listed in [next](#complete-list-of-exposed-variables) section (minus the dependencies part, which does not make sense if you can work in python directly since you can import them yourself).

### Complete list of exposed variables

*Dependencies*

* **json**: python's `json` module.
* **urljoin**: python's `urllib.parse.urljoin`.
* **re**: python's `re` module.
* **soupsieve**: the `soupsieve` module.

*Helpers*

* **parse_date**: function parsing dates (even relative ones such as `53 minutes ago`) and returning them formatted as ISO datetime. Can take a `lang` kwarg if required.

*Local variables*

* **element** *bs4.Tag*: currently selected html element.
* **elements** *list<bs4.Tag>*: html elements being currently iterated over.
* **value** *any*: current output value.

*Context*

* **context** *dict*: local context object (more about this in the next part of this documentation).
* **root** *bs4.Tag*: root element of the html tree.
* **scope** *scope*: a scraper-level global scope object that can be used to track state.

## Accessing global context

When calling a scraper on some html, it is also possible to give the scraper some context, as a `dict`, so that the scraper can use it.

Here is how someone would pass this context in python:

```python
from minet import Scraper

scraper = Scraper('scraper.yml')

scraper(html, context={'important_id': 123, 'nested': {'value': 'hello'}})
```

So, considering this html:

```html
<ul>
  <li>John</li>
  <li>Susan</li>
</ul>
```

You would be able to access the given context by using the `get_context` key, like so:

```yml
---
iterator: li
fields:
  id:
    get_context: important_id
  name: text
```

to return:

```json
[
  {"id": 123, "name": "John"},
  {"id": 123, "name": "Mary"}
]
```

Note that you can give a path instead of a single string to access nested information:

```yml
iterator: li
fields:
  id:
    get_context: important_id
  value:
    get_context: ['nested', 'value'] # could also be written as "nested.value"
  name: text
```

to obtain:

```json
[
  {"id": 123, "value": "hello", "name": "John"},
  {"id": 123, "value": "hello", "name": "Mary"}
]
```

This can be very useful to give access to some extraneous data to the scraper if required. As such when using the `minet scrape` command, useful information is always given to the scraper through context:

* **line** *dict*: the CSV line representing a line in a `minet fetch` report.
* **path** *str*: the path to the html file currently being scraped.
* **basename** *str*: the html file path's base name.

Here is an example where the scraped file's url is added to the output using context:

```yml
---
fields:
  url:
    get_context: line.url
  title:
    sel: title
```

## Defining local context

Sometimes, for clarity or performance, you might want to override global context with some local one, through scraping. Let's consider the following html:

```html
<html>
  <head>
    <title>Last week's posts</title>
  </head>
  <body>
    <ul>
      <li>
        <p>
          Post n°<strong>1</strong> by <em>Allan</em>
        </p>
      </li>
      <li>
        <p>
          Post n°<strong>2</strong> by <em>Susan</em>
        </p>
      </li>
    </ul>
  </body>
</html>
```

If you want to return a list of dicts repeating the title of the document along with each post, you might do it like so:

```yml
---
iterator: li > p
fields:
  title:
    eval: "root.select_one('title').get_text()"
  post:
    sel: strong
  author:
    sel: em
```

and you would obtain:

```json
[
  {"title": "Last week's posts", "post": "1", "author": "Allan"},
  {"title": "Last week's posts", "post": "2", "author": "Susan"},
]
```

but this is not 1. elegant (because you used evaluation) and 2. performant (because you will need to select the `title` tag for each post).

This is when the `set_context` key can be used to alleviate both issues. This key can take a recursive scraper definition and will set keys in a "local" context that will be merged with the global one given to the scraper, at each relevant level.

Here is how we could refactor the previous scraper:

```yml
---
set_context:
  title:
    sel: title
iterator: li > p
fields:
  title:
    get_context: title
  post:
    sel: strong
  author:
    sel: em
```

Finally, note that `set_context` can be used at any level of the scraper's declaration so that this html:

```html
<div data-topic="science">
  <ul>
    <li>
      <p>
        Post n°<strong>1</strong> by <em>Allan</em>
      </p>
    </li>
    <li>
      <p>
        Post n°<strong>2</strong> by <em>Susan</em>
      </p>
    </li>
  </ul>
</div>
<div data-topic="arts">
  <ul>
    <li>
      <p>
        Post n°<strong>3</strong> by <em>Josephine</em>
      </p>
    </li>
    <li>
      <p>
        Post n°<strong>4</strong> by <em>Peter</em>
      </p>
    </li>
  </ul>
</div>
```

could be scraped as:

```json
[
  [
    {"topic": "science", "post": "1", "author": "Allan"},
    {"topic": "science", "post": "2", "author": "Susan"},
  ],
  [
    {"topic": "arts", "post": "3", "author": "Josephine"},
    {"topic": "arts", "post": "4", "author": "Peter"}
  ]
]
```

by using the following declaration:

```yml
---
iterator: div
item:
  set_context:
    topic: data-topic
  iterator: li > p
  fields:
    topic:
      get_context: topic
    post:
      sel: strong
    author:
      sel: em
```

## Aliases

Know that some of the DSL keys have aliases for convenience:

* `sel` can also be written as `$` (which is reminiscent of web development)
* `iterator` can also be written as `$$`

So don't be surprised if you see them appear in people code's sometimes and don't be afraid to use them if they fit your mindset better.

## Scraper execution outline

1. Selection of a single element is made using `sel`, `$` or `sel_eval`.
2. Selection of iteratees is made if `iterator` or `iterator_eval` is present, in which case the scraper output will be a list at this level.
3. `set_context` runs to create a local context.
  1. If we find that we are collecting `fields`, we recurse for each key.
  2. Else we collect our `item` by recursing and finally resolving a leaf directive (i.e. if no sub `iterator`, `iterator_eval`, `item` nor `fields` were given):
     1. If nothing is given, we collect the current html element's text, if a `default` value was not provided instead.
     2. We apply `attr`, or `extract` or `get_context`.
     3. We run `eval`.
     4. If the result is `None`, we set it to the `default` value if provided.
4. If working on a list, we filter values through `filter` or `filter_eval`.
5. If working on a list, we only keep unique items through `uniq`.

## Various useful examples

### Going up the tree

Sometimes it can be useful to move up the tree when selecting elements. Unfortunately, CSS has no mechanism for doing so and I recommend to use evaluation to do so, for the time being.

So considering the following html:

```html
<div data-topic="science">
  <ul>
    <li>
      <p>
        Post n°<strong>1</strong> by <em>Allan</em>
      </p>
    </li>
    <li>
      <p>
        Post n°<strong>2</strong> by <em>Susan</em>
      </p>
    </li>
  </ul>
</div>
<div data-topic="arts">
  <ul>
    <li>
      <p>
        Post n°<strong>3</strong> by <em>Josephine</em>
      </p>
    </li>
    <li>
      <p>
        Post n°<strong>4</strong> by <em>Peter</em>
      </p>
    </li>
  </ul>
</div>
```

you could obtain:

```json
[
  {"topic": "science", "post": "1", "author": "Allan"},
  {"topic": "science", "post": "2", "author": "Susan"},
  {"topic": "arts", "post": "3", "author": "Josephine"},
  {"topic": "arts", "post": "4", "author": "Peter"}
]
```

by using the following scraper:

```yml
iterator: li
fields:
  topic:
    sel_eval: "element.find_parent('div')"
    attr: data-topic
  post:
    sel: p > strong
  author:
    sel: p > em
```
