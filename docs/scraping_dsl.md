# Minet Scraping DSL

## Keywords

* `lambdas`: lambda definitions to precompile.
* `transforms`: transformation chains.
* `settings`: settings.
  * `selection_mode`: xpath or css.
* `scraper`: scraper definition:
  * `iterator`: iterates over the given selector.
  * `iterator_eval`: evaluate the selection on which to iterate.
  * `sel`: defines local selection.
  * `sel_eval`: evaluate a local selection.
  * `item`: defines the value to retrieve.
  * `fields`: defines the fields t@o retrieve.
  * `tabulate`: retrieves from a table. => should be against iterate
  * `extract`: get the text or inner html or outer html etc. or context etc.
  * `attr`: name of attribute to get.
  * `transform`: value transformation chain.
  * `context`: defines local context.
  * `eval`: evaluates an expression to retrieve desired value.
  * `constant`: gives a constant value.

Possibility to pass fields & context in order using an array so they depend on each other?

## Process

1. `sel` or `sel_eval` to refine local selection.
2. `iterator` or `iterator_eval` runs to refine local iterating selection.
3. `context` run to populate.
4. `item` vs `fields` vs `tabulate`.
6. Then => go to 1. => `get` or `attr` or `constant` => `eval` => `transform`.

Test working recursion. Test scrapeTable.

Add limit & slices to iteration. Add filters (filter None by default if only yield).
