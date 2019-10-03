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
  * `item`: defines the value to retrieve. can be a string => attr, if not here equals text extraction.
  * `fields`: defines the fields to retrieve.
  * `tabulate`: retrieves from a table. => should be against iterate
  * `default`: defines a default value. (Could replace `constant`).
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
5. Then => go to 1. => `extract` or `attr` or `constant` => `eval` => `transform`.

Test working recursion. Test scrapeTable.

Add limit & slices to iteration. Add filters (filter None by default if only yield).

## Update CLI

* Need to take scalar vs. list output.
* Need to wire up context.
* Need to try catch process.
* Need to reform the root tree.
* Need to handle jsonl.
* Need to handle yml.
* Need to validate.

* Need to report errors finely.
